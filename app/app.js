/* Samsung Smart TV Legacy widget. ES5 for older WebKit. */
var App = (function () {
  var folders = [
    {name:'\u0424\u0438\u043b\u044c\u043c\u044b', url:'playlists/films.js'},
    {name:'\u041a\u0438\u043d\u043e\u0444\u0438\u043b\u044c\u043c\u044b', url:'playlists/kinofilm.js'},
    {name:'\u041a\u0438\u043d\u043e+', url:'playlists/kino-plus.js'}
  ];
  var channels=[], selected=0, folderSelected=0, playing=null, cache=[null,null,null], positions=[0,0,0];
  var player=null, key=null, widget=null, fullscreen=false, playTimer=null, request=null, generation=0, plugin=null, volumeTimer=null, telegramOpen=false;
  function el(id){return document.getElementById(id);}
  function status(value){el('status').textContent=value || '';}
  function parse(text){
    var lines=text.replace(/^\uFEFF/,'').split(/\r?\n/), result=[], title='', i, line, comma;
    for(i=0;i<lines.length;i++){
      line=lines[i].replace(/^\s+|\s+$/g,'');
      if(line.indexOf('#EXTINF:')===0){comma=line.indexOf(',');title=comma<0?'':line.substring(comma+1).replace(/^\s+|\s+$/g,'');}
      else if(/^https?:\/\//i.test(line)){result.push({name:title || '\u041a\u0430\u043d\u0430\u043b '+(result.length+1),url:line});title='';}
    }
    return result;
  }
  function render(){
    var list=el('list'), tabs=el('tabs'), first=Math.max(0,Math.min(selected-3,channels.length-8)), i, row, number, name, tab;
    tabs.innerHTML='';list.innerHTML='';el('count').textContent='\u041a\u0430\u043d\u0430\u043b\u044b: '+channels.length;
    for(i=0;i<folders.length;i++){
      tab=document.createElement('span');tab.className='tab'+(i===folderSelected?' active':'');tab.textContent=folders[i].name;
      (function(index){tab.onclick=function(){switchTab(index);};})(i);tabs.appendChild(tab);
    }
    for(i=first;i<Math.min(channels.length,first+8);i++){
      row=document.createElement('div');row.className='item'+(i===selected?' active':'');
      number=document.createElement('span');number.className='number';number.textContent=i+1;
      name=document.createElement('span');name.textContent=channels[i].name;row.appendChild(number);row.appendChild(name);
      (function(index){row.onclick=function(){selected=index;render();activate();};})(i);list.appendChild(row);
    }
  }
  function switchTab(index){
    var seq, current, found;
    if(index<0||index>=folders.length)return;
    positions[folderSelected]=selected;
    generation++;seq=generation;if(request)try{request.abort();}catch(e){}request=null;
    folderSelected=index;channels=[];selected=0;render();
    if(cache[index]){
      channels=cache[index].channels;selected=Math.min(positions[index],Math.max(0,channels.length-1));render();status('');return;
    }
    status('\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442\u0430\u2026');
    current=document.createElement('script');request=current;
    current.type='text/javascript';current.charset='UTF-8';
    current.onload=function(){
      if(seq!==generation)return;
      request=null;found=window.SUSHA_PLAYLISTS && window.SUSHA_PLAYLISTS[index];
      if(!found || !found.length){status('\u041f\u043b\u0435\u0439\u043b\u0438\u0441\u0442 \u043e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u0435\u0442 \u0432 \u0441\u0431\u043e\u0440\u043a\u0435.');return;}
      channels=found;cache[index]={channels:found,at:new Date().getTime()};
      selected=Math.min(positions[index],Math.max(0,found.length-1));render();status('');
    };
    current.onerror=function(){if(seq===generation){request=null;status('\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442.');}};
    current.src=folders[index].url;document.body.appendChild(current);

  }
  function setFullscreen(value){fullscreen=value;el('app').className=value?'fullscreen':'';}
  function playbackError(){playing=null;status('\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u043f\u043e\u0442\u043e\u043a. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0441\u0442\u044c \u0438 \u0444\u043e\u0440\u043c\u0430\u0442.');}
  function initializePlayer(){
    var video=document.createElement('video');video.id='tv-video';video.setAttribute('playsinline','playsinline');
    video.style.cssText='width:100%;height:100%;background:#060b10;';
    video.addEventListener('playing',function(){if(playTimer)clearTimeout(playTimer);playTimer=null;if(!request)status('');},false);
    video.addEventListener('error',function(){if(playTimer)clearTimeout(playTimer);playTimer=null;playbackError();},false);
    el('player-container').appendChild(video);player=video;
  }
  function play(){
    if(!channels.length)return;
    if(!player){status('\u041f\u043b\u0435\u0435\u0440 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440\u0430 \u043d\u0435 \u0433\u043e\u0442\u043e\u0432.');return;}
    el('empty').style.display='none';el('now').style.display='block';el('now').textContent=channels[selected].name;
    status('\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435\u2026');playing=channels[selected].url;
    if(playTimer)clearTimeout(playTimer);playTimer=setTimeout(function(){playTimer=null;playbackError();},12000);
    try{player.pause();player.src=channels[selected].url;player.load();player.play();}catch(e){playbackError();}
  }
  function activate(){if(!channels.length){if(!request)switchTab(folderSelected);return;}if(playing===channels[selected].url)setFullscreen(true);else play();}
  function showVolume(audio){
    var box=el('volume-overlay');
    box.textContent=audio.GetUserMute()?'\u0417\u0432\u0443\u043a \u0432\u044b\u043a\u043b\u044e\u0447\u0435\u043d':'\u0413\u0440\u043e\u043c\u043a\u043e\u0441\u0442\u044c: '+audio.GetVolume();
    box.style.display='block';if(volumeTimer)clearTimeout(volumeTimer);
    volumeTimer=setTimeout(function(){box.style.display='none';volumeTimer=null;},2000);
  }
  function openTelegram(){
    var box=el('telegram-dialog'), width=Math.min(window.innerWidth||960,window.screen&&window.screen.width||960), height=Math.min(window.innerHeight||540,window.screen&&window.screen.height||540);
    telegramOpen=true;box.style.left=Math.max(0,Math.floor((width-360)/2))+'px';box.style.top=Math.max(0,Math.floor((height-370)/2))+'px';box.className='';
  }
  function closeTelegram(){telegramOpen=false;el('telegram-dialog').className='hidden';try{el('remote-focus').focus();}catch(ignore){}}
  function onKey(e){
    e=e||window.event;if(!e)return;
    var k=e.keyCode,back=k===10009||(key?k===key.KEY_RETURN:k===27);
    if(key && (k===key.KEY_VOL_UP||k===key.KEY_VOL_DOWN||k===key.KEY_MUTE||k===key.KEY_PANEL_VOL_UP||k===key.KEY_PANEL_VOL_DOWN)){
      var audio=el('plugin-audio'), level;
      e.cancelBubble=true;
      try{
        if(k===key.KEY_MUTE)audio.SetUserMute(audio.GetUserMute()?0:1);
        else{level=audio.GetVolume();audio.SetVolume(Math.max(0,Math.min(100,level+((k===key.KEY_VOL_UP||k===key.KEY_PANEL_VOL_UP)?1:-1))));}
        showVolume(audio);
      }catch(error){}
      return false;
    }
    e.cancelBubble=true;
    var infoKey=k===73||(key&&typeof key.KEY_INFO==='number'&&k===key.KEY_INFO);
    if(telegramOpen){if(back||infoKey||k===13||(key&&k===key.KEY_ENTER))closeTelegram();return false;}
    if(infoKey){openTelegram();return false;}
    if(fullscreen && back){setFullscreen(false);return false;}
    if(fullscreen && !(key&&(k===key.KEY_CH_UP||k===key.KEY_CH_DOWN)))return false;
    if(k===38||(key&&k===key.KEY_UP)){selected=Math.max(0,selected-1);render();return false;}
    if(k===40||(key&&k===key.KEY_DOWN)){selected=Math.min(Math.max(0,channels.length-1),selected+1);render();return false;}
    if(k===13||(key&&(k===key.KEY_ENTER||k===key.KEY_PANEL_ENTER))){activate();return false;}
    if(k===37||(key&&k===key.KEY_LEFT)){if(folderSelected>0)switchTab(folderSelected-1);return false;}
    if(k===39||(key&&k===key.KEY_RIGHT)){if(folderSelected<folders.length-1)switchTab(folderSelected+1);return false;}
    if(back){stop();if(widget)try{widget.sendReturnEvent();}catch(e){}return false;}
    if(channels.length && key && (k===key.KEY_CH_UP||k===key.KEY_CH_DOWN)){
      selected=(selected+(k===key.KEY_CH_UP?1:channels.length-1))%channels.length;render();play();return false;
    }
  }
  function start(){
    try{if(typeof Common!=='undefined')widget=new Common.API.Widget();}catch(e){}
    try{if(typeof Common!=='undefined')key=new Common.API.TVKeyValue();}catch(e){}
    try{if(typeof Common!=='undefined')plugin=new Common.API.Plugin();}catch(e){}
    window.onShow=function(){
      var nav=el('plugin-nnavi'), keys, i;
      try{if(nav && typeof nav.SetBannerState==='function')nav.SetBannerState(1);}catch(e){}
      if(plugin && key){keys=[key.KEY_VOL_UP,key.KEY_VOL_DOWN,key.KEY_MUTE,key.KEY_INFO];for(i=0;i<keys.length;i++)if(typeof keys[i]==='number')try{plugin.registKey(keys[i]);}catch(e){}}
      try{el('remote-focus').focus();}catch(e){}
    };
    try{el('remote-focus').focus();}catch(e){}
    var shortcutWidth=Math.min(window.innerWidth||960,window.screen&&window.screen.width||960);
    el('telegram-shortcut').style.left=Math.max(0,shortcutWidth-205)+'px';
    if(widget)try{widget.sendReadyEvent();}catch(e){}
    selected=0;render();switchTab(0);
    document.onkeydown=function(e){if(document.activeElement!==el('remote-focus'))return onKey(e||window.event);};
    setTimeout(function(){try{initializePlayer();}catch(e){status('\u041f\u043b\u0435\u0435\u0440 \u0442\u0435\u043b\u0435\u0432\u0438\u0437\u043e\u0440\u0430 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u0435\u043d.');}},100);
  }
  function stop(){if(volumeTimer)clearTimeout(volumeTimer);volumeTimer=null;if(playTimer)clearTimeout(playTimer);playTimer=null;playing=null;try{if(player){player.pause();player.removeAttribute('src');player.load();}}catch(e){}}
  return {start:start,stop:stop,parse:parse,onKey:onKey,openTelegram:openTelegram,closeTelegram:closeTelegram};
}());
