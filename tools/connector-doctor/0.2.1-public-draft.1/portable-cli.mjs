#!/usr/bin/env node
import {preferences,planPreferences,handoff,reviewResume,capabilityDrift} from './portability.mjs';
import {readJSON,initializeProfile,loadProfile,applyProfile,rollbackProfile} from './profile-store.mjs';
const [command,...args]=process.argv.slice(2);
try {
  let result;
  if(command==='init'&&args.length===2)result=initializeProfile(args[0],preferences(readJSON(args[1])));
  else if(command==='plan'&&args.length===2)result=planPreferences(loadProfile(args[0]),readJSON(args[1]));
  else if(command==='apply'&&args.length===3&&args[2]==='--consent')result=applyProfile(args[0],readJSON(args[1]),true);
  else if(command==='rollback'&&args.length===3&&args[2]==='--consent')result=rollbackProfile(args[0],args[1],true);
  else if(command==='handoff'&&args.length===1)result=handoff(readJSON(args[0]));
  else if(command==='resume-check'&&args.length===2)result=reviewResume(readJSON(args[0]),readJSON(args[1]));
  else if(command==='drift'&&args.length===3)result=capabilityDrift(readJSON(args[0]),readJSON(args[1]),handoff(readJSON(args[2])).requirements);
  else throw new Error('USAGE');
  console.log(JSON.stringify(result,null,2));
} catch(e) {
  const allowed=new Set(['CONSENT_REQUIRED','DRIFT_CONFLICT','INVALID_METADATA','UNSAFE_WORKSPACE','UNSAFE_FILE','READBACK_FAILED','USAGE']);
  console.error(JSON.stringify({status:allowed.has(e.message)?e.message:'LOCAL_OPERATION_FAILED',host_action_executed:false,local_outcome:['init','apply','rollback'].includes(command)?'UNKNOWN_INSPECT_BEFORE_RETRY':'NO_WRITE_REQUESTED',
    next_action:'Inspect the local profile and backup before retry. No host settings or permissions were changed.'}));
  process.exitCode=1;
}
