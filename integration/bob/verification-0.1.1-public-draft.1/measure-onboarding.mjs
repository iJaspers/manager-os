import {readJSON} from '../../../tools/connector-doctor/0.2.2-public-draft.1/profile-store.mjs';
import {readEvidence} from './evidence-files.mjs';
import {measureJourney} from './onboarding.mjs';
try {
 if(process.argv.length!==4)throw new Error('USAGE');
 const record=readJSON(process.argv[2]);
 const receipt=measureJourney(record,readEvidence(process.argv[3],65536));console.log(JSON.stringify(receipt,null,2));
 if(['HOLD','BLOCKED'].includes(receipt.status))process.exitCode=1;
}catch{console.error('Onboarding evidence missing, invalid or unverified.');process.exitCode=1;}
