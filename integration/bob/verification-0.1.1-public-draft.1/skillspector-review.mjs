/** Review an externally retained SkillSpector 2.12.0 JSON report. Never install. */
import {createHash} from 'node:crypto';
const sha=b=>createHash('sha256').update(b).digest('hex');
const digest=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
export function reviewSkillReport(reportBytes,artifactBytes,receipt){
 const hold=reason=>({status:'HOLD',reason,can_install:false,product_accepted:false});
 if(!Buffer.isBuffer(reportBytes)||reportBytes.length>1048576||!Buffer.isBuffer(artifactBytes)||!artifactBytes.length||artifactBytes.length>2097152)return hold('INVALID_INPUT');
 if(!receipt||receipt.scanner!=='NVIDIA/SkillSpector'||receipt.version!=='2.12.0'||receipt.execution!=='completed'||receipt.isolation!=='external_sandbox_no_network'||receipt.llm_used!==false||receipt.exit_code!==0||!digest(receipt.report_sha256)||!digest(receipt.artifact_sha256)||receipt.report_sha256!==sha(reportBytes)||receipt.artifact_sha256!==sha(artifactBytes))return hold('MISSING_OR_MISMATCHED_SANDBOX_RECEIPT');
 let report;try{report=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(reportBytes));}catch{return hold('INVALID_REPORT');}
 if(report?.execution_successful!==true||report?.metadata?.skillspector_version!=='2.12.0'||report.metadata.llm_requested!==false||!Array.isArray(report.issues)||!Array.isArray(report.components)||report.components.length===0)return hold('INCOMPLETE_REPORT');
 // A score of zero / exit code zero is insufficient. All findings, suppressed
 // findings and analysis limitations still require review; nothing auto-installs.
 const c=report.analysis_completeness;
 if(!c||c.status!=='complete'||c.is_complete!==true||c.execution_successful!==true||c.coverage_percent!==100||!Array.isArray(c.ledger_exceptions)||c.ledger_exceptions.length||!Array.isArray(c.limitations)||c.limitations.length||!Array.isArray(c.scope_exclusions)||c.scope_exclusions.length)return hold('INCOMPLETE_ANALYSIS');
 if(report.issues.length||!Array.isArray(report.suppressed)||report.suppressed.length||report.risk_assessment?.recommendation!=='SAFE')return hold('FINDINGS_REQUIRE_REVIEW');
 return {status:'READY_FOR_HUMAN_REVIEW',can_install:false,product_accepted:false,artifact_sha256:sha(artifactBytes),
  limits:'Receipt/hash consistency only. Authenticate the scanner and sandbox evidence separately; complete licensing, provenance and permission review before installation.'};
}
