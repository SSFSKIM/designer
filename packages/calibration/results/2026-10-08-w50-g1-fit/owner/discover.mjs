// Prospective STATIC source discovery only. Does not execute owner code, read config/data,
// create a root, or seal anything. Its CLI writes one fresh external source list for review.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {builtinModules,createRequire} from 'node:module';
import {dirname,resolve,relative,isAbsolute,basename} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import ts from 'typescript';
const HERE=dirname(fileURLToPath(import.meta.url));
const ROOT=resolve(HERE,'../../../../..');
const source=/\.(?:[cm]?[jt]sx?|py)$/;
const metadata=name=>/^(?:package\.json|tsconfig[^/]*\.json|pnpm-lock\.yaml)$/.test(basename(name));
const inside=(path,root)=>{const rel=relative(root,path);return !rel.startsWith('..')&&!isAbsolute(rel);};

export function discoverSources(root,entries,readers=[]) {
  root=fs.realpathSync(root);
  const pins=new Map(),visited=new Set();
  function add(path) {
    const physical=fs.realpathSync(path);
    if(physical.split('/').includes('node_modules'))return undefined;
    if(!inside(physical,root)||(!source.test(physical)&&!metadata(physical)&&basename(physical)!=='python-shim'))
      throw Error(`Discovery is source-only, refuses: ${physical}`);
    const rel=relative(root,physical),raw=fs.readFileSync(physical);
    const sha256=createHash('sha256').update(raw).digest('hex');
    if(pins.has(rel)&&pins.get(rel)!==sha256)throw Error(`Source changed during discovery: ${rel}`);
    pins.set(rel,sha256);
    for(let dir=dirname(physical);;dir=dirname(dir)) {
      for(const name of ['package.json','tsconfig.json']) {
        const file=resolve(dir,name);
        if(fs.existsSync(file)&&!pins.has(relative(root,file)))add(file);
      }
      if(dir===root)break;
    }
    return {physical,text:raw.toString()};
  }
  function walk(path) {
    const admitted=add(path);
    if(!admitted||visited.has(admitted.physical))return;
    const {physical,text}=admitted;visited.add(physical);
    if(!/\.[cm]?[jt]sx?$/.test(physical))return;
    const ast=ts.createSourceFile(physical,text,ts.ScriptTarget.Latest,true);
    const imports=new Set();
    function visit(node) {
      if((ts.isImportDeclaration(node)||ts.isExportDeclaration(node))&&node.moduleSpecifier) {
        imports.add(node.moduleSpecifier.text);
      } else if(ts.isImportEqualsDeclaration(node)&&ts.isExternalModuleReference(node.moduleReference)) {
        const expression=node.moduleReference.expression;
        if(!expression||!ts.isStringLiteralLike(expression))
          throw Error(`Dynamic import requires a separately declared source edge: ${physical}`);
        imports.add(expression.text);
      } else if(ts.isCallExpression(node)&&(node.expression.kind===ts.SyntaxKind.ImportKeyword||
        (ts.isIdentifier(node.expression)&&node.expression.text==='require'))) {
        if(node.arguments.length!==1||!ts.isStringLiteralLike(node.arguments[0]))
          throw Error(`Dynamic import requires a separately declared source edge: ${physical}`);
        imports.add(node.arguments[0].text);
      }
      ts.forEachChild(node,visit);
    }
    visit(ast);
    for(const specifier of imports) {
      if(specifier.startsWith('node:')||builtinModules.includes(specifier))continue;
      // Reject data edges BEFORE any resolver can open them as a candidate module.
      if(/\.(?:json|png|jpe?g|webp|csv|zip)$/.test(specifier)&&!metadata(specifier))
        throw Error(`Discovery is source-only, refuses import: ${specifier}`);
      // Walk runtime resolution AND TypeScript's declarations. Following only the latter
      // would pin dist/index.d.ts while Node actually executes dist/index.js.
      const targets=new Set();
      try{targets.add(createRequire(pathToFileURL(physical)).resolve(specifier));}catch{}
      const typed=ts.resolveModuleName(specifier,physical,{
        moduleResolution:ts.ModuleResolutionKind.NodeNext,module:ts.ModuleKind.NodeNext,
        allowJs:true,allowImportingTsExtensions:true,customConditions:['source'],
      },ts.sys).resolvedModule?.resolvedFileName;
      if(typed)targets.add(typed);
      if(!targets.size)throw Error(`Unresolved source edge ${specifier} in ${physical}`);
      for(const target of targets)walk(target);
    }
  }
  for(const entry of entries)walk(entry);
  // Named AST readers are data-as-source, not historical modules to execute or import.
  for(const reader of readers)add(reader);
  return {schema:'w50-owner-source-closure-1',discovery:'static imports + explicit AST/source readers',
    pixels:'NONE',sources:[...pins].sort(([a],[b])=>a.localeCompare(b)).map(([path,sha256])=>({path,sha256}))};
}

export function ownerSources() {
  const cal=resolve(ROOT,'packages/calibration');
  const readers=[...['run.py','edge-launch.py','python-shim','edge.py','discover.mjs',
    'metadata.py','byte_witness.py']
    .map(name=>resolve(HERE,name)),resolve(ROOT,'pnpm-lock.yaml'),resolve(ROOT,'tsconfig.base.json'),
    resolve(cal,'test/adopted-thresholds.test.ts'),
    ...['results/2026-10-08-w50-g0-declaration/audit/closure.py',
      'results/2026-10-07-w49a-g0-declaration/seal/seal.ts',
      'results/2026-09-25-w37-g0-edge-identification/canonical.py',
      'results/2026-09-25-w37-g0b-edge-identification/canonical.py',
      'results/2026-09-25-w38-g0-rim-axis-cut/e2.py',
      'results/2026-10-06-w47-g0-operators/cuts/cuts.py'].map(name=>resolve(cal,name))];
  readers.push(resolve(HERE,'../web/vite-guard.mjs'));
  return discoverSources(ROOT,[resolve(HERE,'bridge.ts'),resolve(HERE,'node-guard.mjs')],readers);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  if(process.argv.length!==3)throw Error('Usage: node owner/discover.mjs FRESH_EXTERNAL_SOURCE_LIST');
  const output=process.argv[2];
  if(!isAbsolute(output)||fs.existsSync(output)||inside(fs.realpathSync(dirname(output)),ROOT))
    throw Error('Require fresh external source-only output, never an execution root');
  fs.writeFileSync(output,JSON.stringify(ownerSources(),null,2)+'\n',{flag:'wx'});
}
