/** Fixed public RC1 entry route; page contents never select arbitrary fetch targets. */
import {createHash} from 'node:crypto';
export const ENTRY='https://www.ijaspers.com/post/witburrow-starter-reference';
export const BOB='https://raw.githubusercontent.com/iJaspers/manager-os/main/downloads/BOB_ON_DEMAND_2026.11.01-rc1.txt';
export const BOB_SHA='4fdd30e21c1251623e8bd48d2e001b3b945b533949bfc8fb8dc7ab4441280b1f';
export function checkEntry(html){
 if(typeof html!=='string'||Buffer.byteLength(html)>4194304)return {passed:false,reason:'INVALID_PAGE'};
 const normalized=html.replaceAll('\\/','/').replaceAll('&amp;','&');
 return {passed:normalized.includes(BOB),reason:normalized.includes(BOB)?'RC1_BOB_LINK_IN_HTTP_RESPONSE':'RC1_BOB_LINK_NOT_FOUND',rendered_browser_verified:false};
}
export function checkBob(bytes){
 if(!Buffer.isBuffer(bytes)||bytes.length>65536)return {passed:false,reason:'INVALID_ASSET'};
 const actual=createHash('sha256').update(bytes).digest('hex');
 return {passed:actual===BOB_SHA,bytes:bytes.length,sha256:actual,expected_sha256:BOB_SHA};
}
