// JSON data parser with duplicate-key rejection and bounded nesting.
export function parseStrictJSON(source) {
  let p=0; const whitespace=()=>{while(/[\t\r\n ]/.test(source[p]||'x'))p++;};
  function string(){const start=p++;let escaped=false;while(p<source.length){const c=source[p++];if(c==='"'&&!escaped)return JSON.parse(source.slice(start,p));if(c==='\\'&&!escaped)escaped=true;else escaped=false;}throw Error('Unterminated string');}
  function value(depth=0){
    if(depth>64)throw Error('JSON nesting hold');whitespace();const c=source[p];
    if(c==='"')return string();
    if(c==='{'){p++;const object=Object.create(null),keys=new Set();whitespace();if(source[p]==='}'){p++;return object;}while(true){whitespace();if(source[p]!=='"')throw Error('Object key required');const k=string();if(keys.has(k))throw Error('Duplicate JSON key');keys.add(k);whitespace();if(source[p++]!==':')throw Error('Colon required');object[k]=value(depth+1);whitespace();const end=source[p++];if(end==='}')return object;if(end!==',')throw Error('Comma required');}}
    if(c==='['){p++;const array=[];whitespace();if(source[p]===']'){p++;return array;}while(true){array.push(value(depth+1));whitespace();const end=source[p++];if(end===']')return array;if(end!==',')throw Error('Comma required');}}
    const match=/^(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)/.exec(source.slice(p));
    if(!match)throw Error('Invalid JSON value');p+=match[0].length;const result=JSON.parse(match[0]);if(typeof result==='number'&&!Number.isFinite(result))throw Error('Non-finite number');return result;
  }
  const result=value();whitespace();if(p!==source.length)throw Error('Trailing JSON data');return result;
}
