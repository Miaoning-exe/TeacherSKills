from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel, TypeAdapter, ValidationError

from shared.api_client import AuthenticationError, TeacherSkillsAPIClient, TeacherSkillsAPIError
from shared.schemas.exam import ExamPaper
from shared.schemas.question import Question, QuestionType
from shared.schemas.student import StudentResponse


LOGGER = logging.getLogger(__name__)
ANSWER_SUBMISSION_ADAPTER = TypeAdapter(list["AnswerSubmission"])
STUDENT_RESPONSE_ADAPTER = TypeAdapter(list[StudentResponse])

OBJECTIVE_QUESTION_TYPES = {
    QuestionType.CHOICE,
    QuestionType.FILL_BLANK,
    QuestionType.TRUE_FALSE,
    QuestionType.CLOZE,
    QuestionType.GRAMMAR,
}


class AnswerSubmission(BaseModel):
    student_id: str
    question_id: str
    answer: str


def load_exam(raw_json: str) -> ExamPaper:
    return ExamPaper.model_validate_json(raw_json)


def load_submissions(raw_json: str) -> list[AnswerSubmission]:
    return ANSWER_SUBMISSION_ADAPTER.validate_json(raw_json)


def grade_submissions(
    *,
    exam: ExamPaper,
    submissions: list[AnswerSubmission],
    rubric: str | None = None,
    offline: bool = False,
    api_client: TeacherSkillsAPIClient | None = None,
) -> list[StudentResponse]:
    question_lookup = {
        question.id: question
        for section in exam.sections
        for question in section.questions
    }
    created_client = False
    client = api_client
    if not offline and client is None:
        try:
            client = TeacherSkillsAPIClient()
            created_client = True
        except AuthenticationError as exc:
            LOGGER.info("远程评分不可用，主观题将标记为待评分: %s", exc)
            client = None

    try:
        results: list[StudentResponse] = []
        for submission in submissions:
            question = question_lookup.get(submission.question_id)
            if question is None:
                raise ValueError(f"未在试卷中找到 question_id: {submission.question_id}")
            if _is_objective_question(question):
                results.append(_grade_objective_submission(submission=submission, question=question))
            else:
                results.append(
                    _grade_subjective_submission(
                        submission=submission,
                        question=question,
                        rubric=rubric,
                        api_client=client,
                    )
                )
        return results
    finally:
        if created_client and client is not None:
            client.close()


def responses_to_json(responses: list[StudentResponse]) -> str:
    return STUDENT_RESPONSE_ADAPTER.dump_json(responses, indent=2).decode("utf-8")


def _grade_objective_submission(
    *,
    submission: AnswerSubmission,
    question: Question,
) -> StudentResponse:
    correct = _objective_answers_match(question, submission.answer)
    return StudentResponse(
        student_id=submission.student_id,
        question_id=submission.question_id,
        answer=submission.answer,
        score=question.score if correct else 0.0,
        max_score=question.score,
        feedback="答案正确" if correct else f"答案错误，参考答案：{question.answer}",
    )


def _grade_subjective_submission(
    *,
    submission: AnswerSubmission,
    question: Question,
    rubric: str | None,
    api_client: TeacherSkillsAPIClient | None,
) -> StudentResponse:
    if api_client is None:
        return _pending_response(submission=submission, question=question, reason="待评分：远程评分不可用")
    try:
        result = api_client.grade_subjective_answer(
            question=question,
            student_answer=submission.answer,
            rubric=rubric,
        )
    except TeacherSkillsAPIError as exc:
        LOGGER.warning("远程评分失败，question_id=%s: %s", submission.question_id, exc)
        return _pending_response(submission=submission, question=question, reason=f"待评分：{exc}")

    bounded_score = min(max(result.score, 0.0), question.score)
    return StudentResponse(
        student_id=submission.student_id,
        question_id=submission.question_id,
        answer=submission.answer,
        score=bounded_score,
        max_score=question.score,
        feedback=result.feedback,
    )


def _pending_response(
    *,
    submission: AnswerSubmission,
    question: Question,
    reason: str,
) -> StudentResponse:
    return StudentResponse(
        student_id=submission.student_id,
        question_id=submission.question_id,
        answer=submission.answer,
        score=None,
        max_score=question.score,
        feedback=reason,
    )


def _is_objective_question(question: Question) -> bool:
    return question.question_type in OBJECTIVE_QUESTION_TYPES


def _objective_answers_match(question: Question, actual_answer: str) -> bool:
    expected = _normalize_answer(question, question.answer)
    actual = _normalize_answer(question, actual_answer)
    if question.question_type == QuestionType.CHOICE and question.options:
        option_map = _choice_option_map(question.options)
        return actual == expected or option_map.get(actual) == option_map.get(expected)
    return actual == expected


def _normalize_answer(question: Question, answer: str) -> str:
    normalized = " ".join(answer.strip().split())
    if question.subject == "英语" or question.question_type in {QuestionType.CHOICE, QuestionType.CLOZE, QuestionType.GRAMMAR}:
        return normalized.casefold()
    if question.question_type == QuestionType.TRUE_FALSE:
        return _normalize_true_false(normalized)
    return normalized


def _normalize_true_false(answer: str) -> str:
    mapping = {
        "true": "true",
        "false": "false",
        "对": "true",
        "错": "false",
        "正确": "true",
        "错误": "false",
    }
    return mapping.get(answer.casefold(), answer.casefold())


def _choice_option_map(options: list[str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for option in options:
        prefix, _, content = option.partition(".")
        normalized[prefix.strip().casefold()] = prefix.strip().casefold()
        normalized[option.strip().casefold()] = prefix.strip().casefold()
        if content.strip():
            normalized[content.strip().casefold()] = prefix.strip().casefold()
    return normalized


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="批改学生作答。客观题本地评分，主观题远程评分。")
    parser.add_argument("--exam", required=True, type=Path, help="ExamPaper JSON 文件")
    parser.add_argument("--answers", required=True, type=Path, help="学生作答 JSON 文件")
    parser.add_argument("--output", type=Path, default=None, help="输出 StudentResponse[] JSON 文件")
    parser.add_argument("--rubric-file", type=Path, default=None, help="主观题评分标准文件")
    parser.add_argument("--offline", action="store_true", help="强制离线，只批改客观题")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        exam = load_exam(args.exam.read_text(encoding="utf-8"))
        submissions = load_submissions(args.answers.read_text(encoding="utf-8"))
        rubric = args.rubric_file.read_text(encoding="utf-8") if args.rubric_file else None
        output = responses_to_json(
            grade_submissions(
                exam=exam,
                submissions=submissions,
                rubric=rubric,
                offline=args.offline,
            )
        )
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except (ValidationError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
