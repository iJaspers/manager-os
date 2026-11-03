/** Review already-produced scanner evidence; does not run a scanner or skill. */
import {readJSON} from '../../../tools/connector-doctor/0.2.1-public-draft.1/profile-store.mjs';
import {readEvidence} from './evidence-files.mjs';
import {reviewSkillReport} from './skillspector-review.mjs';
try {
 if(process.argv.length!==5)throw new Error('USAGE');
 const result=reviewSkillReport(readEvidence(process.argv[2],1048576),readEvidence(process.argv[4],2097152),readJSON(process.argv[3]));
 console.log(JSON.stringify(result,null,2));if(result.status==='HOLD')process.exitCode=1;
}catch{console.error('Skill evidence missing, invalid or incomplete. Installation remains blocked.');process.exitCode=1;}
