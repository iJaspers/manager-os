/** Bounded local evidence reads; never follow a final symlink or open a device. */
import {openSync,fstatSync,readSync,closeSync,constants} from 'node:fs';
export function readEvidence(path,limit){
 if(!Number.isSafeInteger(limit)||limit<1||limit>2097152)throw new Error('INVALID_LIMIT');
 let fd;
 try {
  fd=openSync(path,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
  const stat=fstatSync(fd);if(!stat.isFile()||stat.size>limit)throw new Error('INVALID_EVIDENCE');
  const bytes=Buffer.alloc(limit+1);let size=0,n;
  while(size<bytes.length&&(n=readSync(fd,bytes,size,bytes.length-size,null))>0)size+=n;
  if(size>limit)throw new Error('INVALID_EVIDENCE');
  return bytes.subarray(0,size);
 }finally{if(fd!==undefined)closeSync(fd);}
}
