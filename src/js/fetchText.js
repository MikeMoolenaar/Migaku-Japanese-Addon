require("anki/ui").loaded.then(async () => {
  const noteEditor = require("anki/NoteEditor");
  const focusedInputSub = noteEditor.instances[0].focusedInput;

  // Get all anki-editable element so the index of the focused-input can be determined in the next part
  const inputs = [];
  for (let x of noteEditor.instances[0].fields) {
    const element = await x.element;
    const input = element.querySelector(".rich-text-editable").shadowRoot.querySelector("anki-editable");
    inputs.push(input);
  }

  const unsubscribe = focusedInputSub.subscribe(async (x) => {
    const focusedInput = await (x?.element);
    if (!focusedInput) return;
    const fieldText = focusedInput.innerText;
    const fieldIndex = inputs.indexOf(focusedInput);

    pycmd("textToJReading:||:||:" + fieldText + ':||:||:' +  fieldIndex);
  });
  unsubscribe();
})