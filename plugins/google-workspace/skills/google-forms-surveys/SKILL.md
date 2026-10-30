---
name: google-forms-surveys
description: "Create a Google Form (survey, quiz, sign-up, intake or feedback form), edit its questions and settings, publish it, and read or summarise its responses. Use whenever the user asks for a form, survey, questionnaire or quiz in Google Forms, or wants responses from one analysed. Requires google-workspace-mcp (form responses need the form-responses permission)."
---

# Google Forms: build, publish, read responses

Tool signatures in `google-workspace-mcp`: `create_file(type: "form")`, `read_form`,
`update_form`, `publish_form`, `list_form_responses`.

## Build

1. Confirm the goal, audience, whether answers are anonymous, and whether it is a quiz
   (auto-graded) in one message; list the questions you intend to add so the user can edit the
   list before the form exists.
2. `create_file(name, type: "form")` creates an empty form with the title; `read_form` returns
   its `formId`, responder link and settings.
3. Add items with `update_form(formId, requests)`: `createItem: {item: {title, description?,
   questionItem: {question: {required, choiceQuestion: {type: "RADIO"|"CHECKBOX"|"DROP_DOWN",
   options: [{value}], shuffle?}}}}, location: {index: n}}`. Other question kinds:
   `textQuestion: {paragraph: true|false}`, `scaleQuestion: {low, high, lowLabel, highLabel}`,
   `dateQuestion`, `timeQuestion`, `questionGroupItem` (grid). Non-question items:
   `pageBreakItem`, `textItem` (section intro), `imageItem`/`videoItem` (by URL). Items are
   placed and later addressed by 0-based `index`.
4. Settings: `updateSettings` (`quizSettings.isQuiz: true` for quizzes, then
   `question.grading: {pointValue, correctAnswers: {answers: [{value}]}, whenRight/whenWrong
   feedback}` per question); `updateFormInfo` for title/description. Collecting emails or
   limiting to one response per person are form settings not exposed by the API: tell the user
   to set them in the Forms UI.
5. `read_form` to check order, required flags and option lists; fix with `updateItem` /
   `moveItem` / `deleteItem`.
6. `publish_form(formId, published: true, acceptingResponses: true)` when the user wants it
   live; the responder link from `read_form` is what they send out. Share the editor with
   collaborators via `share_file` on the form id if asked.

## Responses

- `list_form_responses(formId, submittedAfter?)` returns each response's answers keyed by
  `questionId` (map them to titles with `read_form`), timestamps, respondent email when the
  form collects it, and quiz scores. Page with `pageToken`; pull everything in `scripted_tools`
  for more than a few dozen responses and aggregate there.
- Summaries: counts per option, mean/median for scales, grouped free-text themes with a few
  verbatim quotes, response rate if the audience size is known. Deliver in chat or, when
  asked, as a Sheet (`build-google-sheet`) or Doc (`write-google-doc`).
- A form linked to a Sheet (`read_form` shows `linkedSheetId`) can also be read with
  `read_sheet`, which is handier for large response sets.

## Gotchas

- File-upload questions cannot be created through the API.
- Closing a form: `publish_form(formId, acceptingResponses: false)` keeps it published but
  stops new responses.
- `list_form_responses` needs the separate form-responses permission; if the tool is missing,
  say so rather than scraping the linked Sheet silently (the Sheet is fine when the user agrees).
