/** Documented Promptfoo custom-provider interface. No model, network or tool execution. */
import {runCase} from './contracts.mjs';
export default class WitContractProvider {
 id(){return 'wit-existing-doctor-contracts';}
 async callApi(prompt){
  try{return {output:JSON.stringify(runCase(prompt)),metadata:{evidence_kind:'SYNTHETIC_CONTRACT',native_host_tested:false}};}
  catch{return {error:'UNKNOWN_CASE'};}
 }
}
