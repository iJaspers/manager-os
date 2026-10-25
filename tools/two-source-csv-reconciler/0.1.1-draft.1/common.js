"use strict";
// Entire toolkit is client-side only. No network, storage or external libraries.
function $(id){return document.getElementById(id)}
function field(id){return $(id).value.trim()}
function money(cents){return new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD'}).format(cents/100)}
function toCents(value){const s=String(value).trim();if(!/^(?:\d+)(?:\.\d{1,2})?$/.test(s))return null;const [whole,frac='']=s.split('.');const n=Number(whole)*100+Number(frac.padEnd(2,'0'));return Number.isSafeInteger(n)?n:null}
function percentOf(cents,percent){return Math.round(cents*percent/100)}
function downloadText(name,text,type='text/plain;charset=utf-8'){const a=document.createElement('a');const u=URL.createObjectURL(new Blob([text],{type}));a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500)}
function escapeCSV(s){s=String(s??''); // protect against formula injection in spreadsheet applications
if(/^[\s]*[=+@\-\t\r]/.test(s))s="'"+s;
return '"'+s.replace(/"/g,'""')+'"'}
function csvSerialize(rows){return rows.map(r=>r.map(escapeCSV).join(',')).join('\r\n')+'\r\n'}
// RFC 4180-style quoted fields, embedded commas, newlines and escaped quotes.
function parseCSV(text){const rows=[];let row=[],cell='',quoted=false,endedQuote=false;for(let i=0;i<text.length;i++){const c=text[i];if(quoted){if(c==='"'){if(text[i+1]==='"'){cell+='"';i++}else{quoted=false;endedQuote=true}}else{cell+=c}}else if(c==='"' && cell==='' && !endedQuote){quoted=true}else if(c==='"'){throw Error('Unexpected quote in unquoted field at character '+(i+1))}else if(c===','){row.push(cell);cell='';endedQuote=false}else if(c==='\n'||c==='\r'){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(x=>x.trim()!==''))rows.push(row);row=[];cell='';endedQuote=false}else if(endedQuote&&c!==' '&&c!=='\t'){throw Error('Unexpected character after closing quote at character '+(i+1))}else if(!endedQuote){cell+=c}}if(quoted)throw Error('Unclosed quoted field');if(cell!==''||row.length){row.push(cell);if(row.some(x=>x.trim()!==''))rows.push(row)}return rows}
