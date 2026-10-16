'use strict';
let albums = [], filter = 'all';
const $ = id => document.getElementById(id);
function notice(message, error = false) { $('notice').textContent = message; $('notice').className = error ? 'error' : ''; }
async function api(path, options) {
  const response = await fetch('/api' + path, options);
  if (!response.ok) {
    let message = 'Request failed (' + response.status + '). Please try again.';
    try { const data = await response.json(); if (typeof data.detail === 'string') message = data.detail; } catch (_) {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}
function el(tag, className, text) { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; }
async function change(id, payload) {
  try { await api('/albums/' + id, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}); await load(); notice('Listening journal updated.'); }
  catch (error) { notice(error.message, true); }
}
function render() {
  const query = $('search').value.trim().toLowerCase();
  const visible = albums.filter(a => (filter === 'all' || a.status === filter) && (a.title + ' ' + a.artist).toLowerCase().includes(query));
  $('total').textContent = albums.length;
  $('queued').textContent = albums.filter(a => a.status === 'queued').length;
  $('listened').textContent = albums.filter(a => a.status === 'listened').length;
  const rated = albums.filter(a => a.rating !== null);
  $('average').textContent = rated.length ? (rated.reduce((s,a) => s + a.rating, 0) / rated.length).toFixed(1) + ' / 5' : '-';
  $('count').textContent = visible.length;
  $('list').replaceChildren();
  if (!visible.length) { $('list').append(el('p','empty',albums.length ? 'No albums match this view.' : 'Your next favorite record starts here. Queue your first album above.')); return; }
  for (const album of visible) {
    const card = el('article','album');
    const cover = el('div','cover',album.title.slice(0,1).toUpperCase()); cover.setAttribute('aria-hidden','true'); card.append(cover);
    const body = el('div','album-body'); body.append(el('h3','',album.title),el('p','artist',album.artist + (album.year ? ' · ' + album.year : '')));
    const controls = el('div','album-controls'); const select = el('select'); select.setAttribute('aria-label','Listening status for ' + album.title);
    for (const status of ['queued','listening','listened']) { const option = el('option','',status[0].toUpperCase()+status.slice(1)); option.value=status; option.selected=status===album.status; select.append(option); }
    select.addEventListener('change',()=>change(album.id,{status:select.value})); controls.append(select);
    const remove = el('button','delete','Remove'); remove.setAttribute('aria-label','Remove '+album.title);
    remove.addEventListener('click',async()=>{ if (!confirm('Remove "'+album.title+'" from your journal?')) return; try {await api('/albums/'+album.id,{method:'DELETE'});await load();notice('Album removed.');} catch(error){notice(error.message,true);} }); controls.append(remove);body.append(controls);
    const stars=el('div','rating');stars.setAttribute('aria-label','Album rating');
    for(let n=1;n<=5;n++){const button=el('button','',n<=(album.rating||0)?'★':'☆');button.setAttribute('aria-label','Rate '+album.title+' '+n+' out of 5');button.setAttribute('aria-pressed',String(n===album.rating));button.addEventListener('click',()=>change(album.id,{rating:n}));stars.append(button);}body.append(stars);card.append(body);$('list').append(card);
  }
}
async function load(){ $('list').setAttribute('aria-busy','true');try{albums=await api('/albums');render();}catch(error){$('list').replaceChildren(el('p','empty','Your collection could not load. Check that the API and database are running.'));notice(error.message,true);}finally{$('list').setAttribute('aria-busy','false');}}
$('add').addEventListener('submit',async event=>{event.preventDefault();const title=$('title').value.trim(),artist=$('artist').value.trim();if(!title||!artist){notice('Add an album title and artist.',true);return;}$('add-button').disabled=true;try{await api('/albums',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,artist,year:$('year').value?Number($('year').value):null})});event.target.reset();await load();notice('Album added to your queue.');}catch(error){notice(error.message,true);}finally{$('add-button').disabled=false;}});
$('search').addEventListener('input',render);
for(const button of document.querySelectorAll('[data-filter]')){button.addEventListener('click',()=>{filter=button.dataset.filter;for(const b of document.querySelectorAll('[data-filter]')){b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));}render();});}
load();
