require("anki/ui").loaded.then(async () => {
  const noteEditor = require("anki/NoteEditor");
  const focusedInputSub = noteEditor.instances[0].focusedInput;

  const unsubscribe = focusedInputSub.subscribe(async (x) => {
    const focusedInput = await (x?.element);
    if (!focusedInput) return;
    focusedInput.innerHTML = '%s';
  });
  unsubscribe();
});