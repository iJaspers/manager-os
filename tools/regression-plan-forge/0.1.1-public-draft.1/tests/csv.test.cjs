// MIT; parser vectors inherited from WIT Reconciler 0.1.2. See PROVENANCE.json.
const test=require('node:test'),assert=require('node:assert/strict');
const {parseCSV,csvSerialize}=require('../common.js');
const valid = [
 ['plain rows','a,b\n1,two',[['a','b'],['1','two']]],
 ['quoted commas','a,b\n1,"blue,green"',[['a','b'],['1','blue,green']]],
 ['doubled quotes','a,b\n1,"say ""hello"""',[['a','b'],['1','say "hello"']]],
 ['embedded LF','a,b\n1,"first\nsecond"',[['a','b'],['1','first\nsecond']]],
 ['embedded CRLF','a,b\r\n1,"first\r\nsecond"\r\n',[['a','b'],['1','first\r\nsecond']]],
 ['embedded CR','a,b\r1,"first\rsecond"\r',[['a','b'],['1','first\rsecond']]],
 ['quoted empty field','a,b\n1,""',[['a','b'],['1','']]],
 ['empty middle field','a,b,c\n1,,3',[['a','b','c'],['1','','3']]],
 ['empty final field','a,b,c\n1,two,',[['a','b','c'],['1','two','']]],
 ['empty initial field','a,b\n,two',[['a','b'],['','two']]],
 ['all quoted headers','"a","b"\n"1","two"',[['a','b'],['1','two']]],
 ['space after closing quote preserved compatibility','a,b\n1,"two" \t',[['a','b'],['1','two']]],
 ['space before delimiter after quoted field','a,b\n"1" \t,"two"',[['a','b'],['1','two']]],
 ['unquoted spaces preserved','a,b\n 1 , two ',[['a','b'],[' 1 ',' two ']]],
 ['Unicode','a,b\n1,"é😀漢字"',[['a','b'],['1','é😀漢字']]],
 ['single quote content','a,b\n1,it\'s fine',[['a','b'],['1',"it's fine"]]],
 ['one literal double quote','a,b\n1,""""',[['a','b'],['1','"']]],
 ['two literal double quotes','a,b\n1,""""""',[['a','b'],['1','""']]],
 ['blank lines ignored compatibility','\n\r\na,b\n\n1,two\n',[['a','b'],['1','two']]],
 ['quoted blank row ignored compatibility','a,b\n" ","\t"\n1,two',[['a','b'],['1','two']]],
 ['empty input','',[]],
 ['header only','a,b',[['a','b']]],
 ['comma and newline inside quoted field','a,b\n1,"left,\nright"',[['a','b'],['1','left,\nright']]],
 ['formula-shaped input remains inert text','a,b\n1,=1+1',[['a','b'],['1','=1+1']]],
 ];
const invalid = [
 ['bare quote middle','a,b\n1,ab"cd'],
 ['bare quote at end','a,b\n1,ab"'],
 ['bare quote first row','ab"cd,b\n1,two'],
 ['bare quote followed by comma','a,b\n1,ab",'],
 ['bare quote followed by newline','a,b\n1,ab"\n'],
 ['two bare quotes','a,b\n1,ab""cd'],
 ['quote after unquoted space','a,b\n1, "two"'],
 ['quote after unquoted tab','a,b\n1,\t"two"'],
 ['unclosed quoted field','a,b\n1,"two'],
 ['unclosed escape sequence','a,b\n1,"two""'],
 ['character immediately after quote','a,b\n1,"two"x'],
 ['character after closing quote whitespace','a,b\n1,"two" x'],
 ['quote after closing quote whitespace','a,b\n1,"two" "'],
 ['bare quote after previous quoted row','a,b\n1,"good"\n2,bad"row'],
 ['bare quote after earlier empty field','a,b,c\n1,,bad"row'],
 ];

for(const [name,input,expected] of valid)test('CSV '+name,()=>assert.deepEqual(parseCSV(input),expected));
for(const [name,input] of invalid)test('CSV rejects '+name,()=>assert.throws(()=>parseCSV(input),/quote|quoted/i));
for(const prefix of ['=1+1','+1','-1','@SUM(A1)','\t=1','\r=1','  =1'])test('formula-safe export '+JSON.stringify(prefix),()=>assert.equal(parseCSV(csvSerialize([[prefix]]))[0][0],"'"+prefix));
test('serializer roundtrip',()=>{const rows=[['id','value'],['R-1','comma, value'],['R-2','say "hello"'],['R-3','multi\nline'],['R-4','Unicode é😀']];assert.deepEqual(parseCSV(csvSerialize(rows)),rows);});
