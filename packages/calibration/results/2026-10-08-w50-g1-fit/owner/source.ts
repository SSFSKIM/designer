import ts from 'typescript';
import { createHash } from 'node:crypto';

const factories = new Map<string, Function>();

/** AST selection, not text scraping. The caller pins the whole owner file and explicitly
 * names every declaration/dependency. No imports, test registrations or data reads execute.
 * Scope selectors use the describe title before '/', avoiding homonymous local constants.
 */
export function bindSource(text: string, expectedSha256: string, selectors: readonly string[],
  bindings: Record<string, unknown> = {}): Record<string, any> {
  if (createHash('sha256').update(text).digest('hex') !== expectedSha256) {
    throw new Error('Owner source hash changed');
  }
  const cacheKey = JSON.stringify([expectedSha256, selectors, Object.keys(bindings)]);
  const cached = factories.get(cacheKey);
  if (cached) return cached(...Object.values(bindings));
  const source = ts.createSourceFile('owner.ts', text, ts.ScriptTarget.Latest, true);
  const found = new Map<string, string[]>();
  const add = (key: string, code: string) => found.set(key, [...(found.get(key) ?? []), code]);
  function visit(node: ts.Node, scope = ''): void {
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression)
      && node.expression.text === 'describe' && ts.isStringLiteral(node.arguments[0]!)) {
      const title = (node.arguments[0] as ts.StringLiteral).text;
      const callback = node.arguments[1];
      if (callback && ts.isArrowFunction(callback)) visit(callback.body, title);
      return;
    }
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression)
      && node.expression.text === 'it' && ts.isStringLiteral(node.arguments[0]!)) {
      const title = (node.arguments[0] as ts.StringLiteral).text;
      const callback = node.arguments[1];
      // A test-local constant requires its exact test title in the selector. Only its
      // declaration can be emitted: neither the test callback nor its assertions execute.
      if (callback && ts.isArrowFunction(callback)) visit(callback.body, `${scope}/it:${title}`);
      return;
    }
    if (ts.isVariableStatement(node)) {
      for (const declaration of node.declarationList.declarations) {
        if (ts.isIdentifier(declaration.name)) {
          add((scope ? scope + '/' : '') + declaration.name.text,
            'const ' + declaration.getText(source) + ';');
        }
      }
      return;
    }
    if (ts.isFunctionDeclaration(node) && node.name) {
      add((scope ? scope + '/' : '') + node.name.text, node.getText(source));
      return;
    }
    // Other executable calls are not declaration scopes.
    if (ts.isCallExpression(node)) return;
    ts.forEachChild(node, child => visit(child, scope));
  }
  visit(source);
  const names = selectors.map(s => s.slice(s.lastIndexOf('/') + 1));
  if (new Set([...names, ...Object.keys(bindings)]).size !== names.length + Object.keys(bindings).length) {
    throw new Error('Duplicate owner binding');
  }
  const code = selectors.map(selector => {
    const entries = found.get(selector);
    if (entries?.length !== 1) throw new Error(`Missing/ambiguous owner symbol ${selector}`);
    return entries[0];
  }).join('\n');
  const js = ts.transpileModule(code, { compilerOptions: { target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.None } }).outputText;
  // Check the emitted JS: erased type names are irrelevant, but a free runtime dependency
  // is a protocol defect even when it lives in a function that has not yet been called.
  const file = '/__w50_owner_closure__.js';
  const check = [...Object.keys(bindings).map(k => `var ${k};`), js].join('\n');
  const options: ts.CompilerOptions = { allowJs: true, checkJs: true, noEmit: true,
    target: ts.ScriptTarget.ES2022, types: [] };
  const host = ts.createCompilerHost(options);
  const getSourceFile = host.getSourceFile.bind(host);
  host.getSourceFile = (name, language, ...rest) => name === file
    ? ts.createSourceFile(file, check, language, true, ts.ScriptKind.JS)
    : getSourceFile(name, language, ...rest);
  const program = ts.createProgram([file], options, host);
  const unresolved = program.getSemanticDiagnostics().filter(d => [2304, 2552, 2580].includes(d.code));
  if (unresolved.length) throw new Error('Unbound owner dependency: ' + unresolved.map(d =>
    ts.flattenDiagnosticMessageText(d.messageText, ' ')).join('; '));
  const factory = new Function(...Object.keys(bindings), js + `\nreturn {${names.join(',')}};`);
  factories.set(cacheKey, factory);
  return factory(...Object.values(bindings));
}

/** A few owner bounds occur only as literal equality assertions rather than exported constants.
 * Read their AST, requiring one numeric assertion per exact subject, without running the test. */
export function assertedNumbers(text:string, expectedSha256:string, subjects:readonly string[]) {
  if(createHash('sha256').update(text).digest('hex')!==expectedSha256) throw new Error('Owner source hash changed');
  const source=ts.createSourceFile('owner.ts',text,ts.ScriptTarget.Latest,true);
  const found=new Map<string,number[]>();
  function visit(node:ts.Node) {
    if(ts.isCallExpression(node)&&ts.isPropertyAccessExpression(node.expression)
      &&node.expression.name.text==='toBe'&&ts.isCallExpression(node.expression.expression)) {
      const expectation=node.expression.expression;
      if(ts.isIdentifier(expectation.expression)&&expectation.expression.text==='expect'
        &&expectation.arguments[0]&&node.arguments[0]&&ts.isNumericLiteral(node.arguments[0])) {
        const subject=expectation.arguments[0].getText(source);
        if(subjects.includes(subject)) found.set(subject,[...(found.get(subject)??[]),Number(node.arguments[0].text)]);
      }
    }
    ts.forEachChild(node,visit);
  }
  visit(source);
  return Object.fromEntries(subjects.map(subject=>{
    const values=found.get(subject);
    if(values?.length!==1) throw new Error(`Missing/ambiguous owner bound ${subject}`);
    return [subject,values[0]!];
  }));
}
