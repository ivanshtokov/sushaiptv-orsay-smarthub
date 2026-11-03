/* Regression for Samsung's overlapping Mute / Escape key codes. */
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');
let exits = 0;
const registered = [];
let volume = 15, mute = 0;
function element() {
  return {className:'', textContent:'', style:{}, innerHTML:'', appendChild(){}, focus(){}};
}
const elements = {'plugin-audio': {GetVolume(){return volume;}, SetVolume(n){volume=n;}, GetUserMute(){return mute;}, SetUserMute(n){mute=n;}}};
const document = {body:{appendChild(){}}, activeElement:null, getElementById(id){return elements[id] || (elements[id]=element());}, createElement(){return element();}};
function Widget(){this.sendReadyEvent = function(){};this.sendReturnEvent = function(){exits++;};}
function TVKeyValue(){this.KEY_MUTE=27;this.KEY_RETURN=88;this.KEY_VOL_UP=7;this.KEY_VOL_DOWN=11;this.KEY_PANEL_VOL_UP=203;this.KEY_PANEL_VOL_DOWN=204;this.KEY_INFO=31;}
function Plugin(){this.registKey = function(k){registered.push(k);};}
function XMLHttpRequest(){this.open=function(){};this.send=function(){};}
const context = {document, window:{}, Common:{API:{Widget,TVKeyValue,Plugin}}, XMLHttpRequest, setTimeout(){}, clearTimeout(){}, Date};
vm.runInNewContext(fs.readFileSync('app/app.js','utf8'), context);
context.App.start();context.window.onShow();
assert.deepStrictEqual(registered,[7,11,27,31]);
for (const code of [7,11,27,203,204]) {
  const event={keyCode:code};
  assert.strictEqual(context.App.onKey(event),false);
  assert.strictEqual(event.cancelBubble,true);
}
assert.strictEqual(volume,15,'Volume up/down must balance');
assert.strictEqual(elements['volume-overlay'].style.display,'block');
assert.strictEqual(mute,1,'Mute must toggle audio');
assert.strictEqual(exits,0,'Mute must not exit the application');
assert.strictEqual(context.App.onKey({keyCode:31}),false);
assert.strictEqual(elements['telegram-dialog'].className,'','Info must open the QR dialog');
assert.strictEqual(context.App.onKey({keyCode:88}),false);
assert.strictEqual(elements['telegram-dialog'].className,'hidden','Return must close the QR dialog');
assert.strictEqual(exits,0,'Closing the QR must not exit the widget');
assert.strictEqual(context.App.onKey({keyCode:88}),false);
assert.strictEqual(exits,1,'Return must still exit from the channel list');
console.log('remote key regression: OK');
