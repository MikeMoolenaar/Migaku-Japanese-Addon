function wrapSelection(selection) {
    var selection = selection.parentNode.getSelection();
    if(selection.toString().length < 2) 
      return [selection.anchorNode, selection.anchorOffset, false,false];
    if (selection.getRangeAt && selection.rangeCount) {
        var range = selection.getRangeAt(0);
        return [range.startContainer,range.startOffset, range.endContainer, range.endOffset];
    }
}

function fetchIndividual(cur, fieldIndex) {
  var ogHTML = cur.innerHTML;
  var startCont, startOff, endCont, endOff;
  [startCont, startOff,endCont, endOff] = wrapSelection(cur);
  if(endCont){
    var offset = 0;
    if(startCont.isSameNode(endCont)) offset = 7;
    startCont.textContent = startCont.textContent.substring(0,startOff) + '--IND--' + startCont.textContent.substring(startOff);
    endCont.textContent = endCont.textContent.substring(0,endOff + offset) + '--IND--' + endCont.textContent.substring(endOff + offset);
  }else{
    startCont.textContent = startCont.textContent.substring(0,startOff) + '--IND--' + startCont.textContent.substring(startOff);
  }
  pycmd("individualJExport:||:||:" + cur.innerHTML + ':||:||:' +  fieldIndex);
}

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
    const fieldIndex = inputs.indexOf(focusedInput);

    fetchIndividual(focusedInput, fieldIndex);
  });
  unsubscribe();
})