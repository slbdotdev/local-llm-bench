class MiniError(Exception):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


_RES = {'let','letrec','and','in','if','then','else','fun','match','with','end','ref','true','false'}
_OPS = ['->', ':=', '==', '!=', '<=', '>=', '&&', '||', '++', '+', '-', '*', '/', '%', '<', '>', '=', '(', ')', '{', '}', ',', '.', '|', '!']


def _lex(s):
    if not isinstance(s, str):
        raise MiniError('parse')
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n': i += 1; continue
        if c == '"':
            j = i + 1
            while j < n and s[j] not in '"\\\r\n': j += 1
            if j >= n or s[j] != '"': raise MiniError('parse')
            out.append(('str', s[i+1:j])); i = j + 1; continue
        if '0' <= c <= '9':
            j = i + 1
            while j < n and '0' <= s[j] <= '9': j += 1
            if j - i > 1 and c == '0': raise MiniError('parse')
            value = 0
            for d in s[i:j]: value = value * 10 + (ord(d) - 48)
            out.append(('int', value)); i = j; continue
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or c == '_':
            j = i + 1
            while j < n and (('A' <= s[j] <= 'Z') or ('a' <= s[j] <= 'z') or ('0' <= s[j] <= '9') or s[j] == '_'): j += 1
            w = s[i:j]
            out.append(('_' if w == '_' else (w if w in _RES else 'id'), w)); i = j; continue
        found = None
        for op in _OPS:
            if s.startswith(op, i): found = op; break
        if found is None: raise MiniError('parse')
        out.append((found, found)); i += len(found)
    out.append(('EOF', None)); return out


class _Parser:
    def __init__(self, s): self.t = _lex(s); self.i = 0
    def k(self): return self.t[self.i][0]
    def take(self, k=None):
        if k is not None and self.k() != k: raise MiniError('parse')
        x = self.t[self.i]; self.i += 1; return x
    def ident(self):
        if self.k() != 'id': raise MiniError('parse')
        return self.take()[1]
    def expr(self):
        k = self.k()
        if k == 'let':
            self.take(); name = self.ident(); self.take('='); rhs = self.expr(); self.take('in'); body = self.expr()
            return ('let', name, rhs, body)
        if k == 'letrec':
            self.take(); bs = []
            while True:
                name = self.ident(); self.take('='); bs.append((name, self.expr()))
                if self.k() != 'and': break
                self.take()
            self.take('in'); body = self.expr()
            names = [x[0] for x in bs]
            if len(set(names)) != len(names): raise MiniError('dup_binding')
            return ('letrec', bs, body)
        if k == 'if':
            self.take(); c = self.expr(); self.take('then'); a = self.expr(); self.take('else'); b = self.expr()
            return ('if', c, a, b)
        if k == 'fun':
            self.take(); p = self.ident(); self.take('->'); return ('fun', p, self.expr())
        if k == 'match':
            self.take(); e = self.expr(); self.take('with'); arms = []
            while self.k() == '|':
                self.take(); p, names = self.pattern()
                if len(names) != len(set(names)): raise MiniError('dup_binding')
                self.take('->'); arms.append((p, self.expr()))
            self.take('end'); return ('match', e, arms)
        return self.assign()
    def assign(self):
        x = self.orx()
        if self.k() == ':': raise MiniError('parse')
        if self.k() == ':=': self.take(); return ('assign', x, self.expr())
        return x
    def orx(self):
        x = self.andx()
        while self.k() == '||': self.take(); x = ('bin','||',x,self.andx())
        return x
    def andx(self):
        x = self.cmpx()
        while self.k() == '&&': self.take(); x = ('bin','&&',x,self.cmpx())
        return x
    def cmpx(self):
        x = self.catx()
        if self.k() in ('==','!=','<','<=','>','>='):
            op=self.take()[0]; x=('bin',op,x,self.catx())
            if self.k() in ('==','!=','<','<=','>','>='): raise MiniError('parse')
        return x
    def catx(self):
        x=self.addx()
        if self.k() == '++': self.take(); x=('bin','++',x,self.catx())
        return x
    def addx(self):
        x=self.mulx()
        while self.k() in ('+','-'): op=self.take()[0]; x=('bin',op,x,self.mulx())
        return x
    def mulx(self):
        x=self.unary()
        while self.k() in ('*','/','%'): op=self.take()[0]; x=('bin',op,x,self.unary())
        return x
    def unary(self):
        if self.k() in ('-','!','ref'): op=self.take()[0]; return ('un',op,self.unary())
        return self.app()
    def app(self):
        x=self.postfix()
        while self.k() in ('int','str','id','true','false','(','{'):
            x=('app',x,self.postfix())
        return x
    def postfix(self):
        x=self.atom()
        while self.k() == '.': self.take(); x=('field',x,self.ident())
        return x
    def atom(self):
        k=self.k()
        if k == 'int': return ('lit',self.take()[1])
        if k == 'str': return ('lit',self.take()[1])
        if k in ('true','false'): self.take(); return ('lit',k == 'true')
        if k == 'id': return ('var',self.take()[1])
        if k == '(':
            self.take(); x=self.expr(); self.take(')'); return x
        if k == '{': return self.record()
        raise MiniError('parse')
    def record(self):
        self.take('{'); fs=[]
        if self.k() != '}':
            while True:
                name=self.ident(); self.take('='); fs.append((name,self.expr()))
                if self.k() != ',': break
                self.take(',')
        self.take('}')
        names=[x[0] for x in fs]
        if len(names) != len(set(names)): raise MiniError('dup_field')
        return ('record',fs)
    def pattern(self):
        k=self.k()
        if k == '_': self.take(); return (('_',), [])
        if k == 'int' or k == 'str': return (('lit',self.take()[1]), [])
        if k in ('true','false'): self.take(); return (('lit',k == 'true'), [])
        if k == 'id':
            name=self.take()[1]; return (('bind',name), [name])
        if k == '{':
            self.take(); fs=[]
            if self.k() != '}':
                while True:
                    name=self.ident(); self.take('='); p, ns=self.pattern(); fs.append((name,p,ns))
                    if self.k() != ',': break
                    self.take(',')
            self.take('}')
            names=[f[0] for f in fs];
            if len(names) != len(set(names)): raise MiniError('dup_field')
            alln=[]
            for _,_,ns in fs: alln.extend(ns)
            return (('recordpat',[(a,b) for a,b,_ in fs]), alln)
        raise MiniError('parse')


class _Slot:
    def __init__(self, value=None): self.value=value; self.init=value is not None
class _Env:
    def __init__(self, parent=None, vals=None): self.parent=parent; self.vals={} if vals is None else vals
    def get(self,n):
        if n in self.vals:
            v=self.vals[n]
            if isinstance(v,_Slot) and not v.init: raise MiniError('uninit')
            return v.value if isinstance(v,_Slot) else v
        if self.parent is not None: return self.parent.get(n)
        raise MiniError('unbound')
class _Closure:
    def __init__(self,p,b,e): self.p=p; self.b=b; self.e=e
class _Ref:
    def __init__(self,v): self.v=v

def _isint(x): return isinstance(x,int) and not isinstance(x,bool)
def _ev(a,e):
    tag=a[0]
    if tag=='lit': return a[1]
    if tag=='var': return e.get(a[1])
    if tag=='fun': return _Closure(a[1],a[2],e)
    if tag=='let': return _ev(a[3],_Env(e,{a[1]:_ev(a[2],e)}))
    if tag=='letrec':
        slots={n:_Slot() for n,_ in a[1]}; ne=_Env(e,slots)
        for n,r in a[1]: slots[n].value=_ev(r,ne); slots[n].init=True
        return _ev(a[2],ne)
    if tag=='if':
        c=_ev(a[1],e)
        if not isinstance(c,bool): raise MiniError('type')
        return _ev(a[2] if c else a[3],e)
    if tag=='record':
        return {n:_ev(x,e) for n,x in a[1]}
    if tag=='field':
        v=_ev(a[1],e)
        if not isinstance(v,dict): raise MiniError('type')
        if a[2] not in v: raise MiniError('no_field')
        return v[a[2]]
    if tag=='app':
        f=_ev(a[1],e); x=_ev(a[2],e)
        if not isinstance(f,_Closure): raise MiniError('type')
        return _ev(f.b,_Env(f.e,{f.p:x}))
    if tag=='un':
        v=_ev(a[2],e); op=a[1]
        if op=='ref': return _Ref(v)
        if op=='-' and _isint(v): return -v
        if op=='!' and isinstance(v,_Ref): return v.v
        raise MiniError('type')
    if tag=='assign':
        x=_ev(a[1],e); y=_ev(a[2],e)
        if not isinstance(x,_Ref): raise MiniError('type')
        x.v=y; return y
    if tag=='bin': return _bin(a[1],a[2],a[3],e)
    if tag=='match':
        v=_ev(a[1],e)
        for p,b in a[2]:
            binds={}
            if _match(p,v,binds): return _ev(b,_Env(e,binds))
        raise MiniError('no_match')
    raise MiniError('parse')

def _bin(op,l,r,e):
    x=_ev(l,e)
    if op=='&&':
        if not isinstance(x,bool): raise MiniError('type')
        if not x: return False
        y=_ev(r,e)
        if not isinstance(y,bool): raise MiniError('type')
        return y
    if op=='||':
        if not isinstance(x,bool): raise MiniError('type')
        if x: return True
        y=_ev(r,e)
        if not isinstance(y,bool): raise MiniError('type')
        return y
    y=_ev(r,e)
    if op in ('+','-','*','/','%'):
        if op=='*' and isinstance(x,str) and _isint(y): return x * max(0,y)
        if not (_isint(x) and _isint(y)): raise MiniError('type')
        if op=='+': return x+y
        if op=='-': return x-y
        if op=='*': return x*y
        if y==0: raise MiniError('div_zero')
        if op=='/': return (abs(x)//abs(y)) * (-1 if (x<0) != (y<0) else 1)
        q=(abs(x)//abs(y)) * (-1 if (x<0) != (y<0) else 1)
        if x != q*y and ((x < 0) != (y < 0)): q -= 1
        return x-q*y
    if op=='++':
        if not isinstance(x,str): raise MiniError('type')
        if isinstance(y,str): return x+y
        if _isint(y): return x+str(y)
        if isinstance(y,bool): return x+('true' if y else 'false')
        raise MiniError('type')
    if op in ('<','<=','>','>='):
        if not (( _isint(x) and _isint(y)) or (isinstance(x,str) and isinstance(y,str))): raise MiniError('type')
        return {'<':x<y,'<=':x<=y,'>':x>y,'>=':x>=y}[op]
    if op in ('==','!='):
        good=(_isint(x) and _isint(y)) or (isinstance(x,str) and isinstance(y,str)) or (isinstance(x,bool) and isinstance(y,bool)) or (isinstance(x,_Ref) and isinstance(y,_Ref))
        if not good: raise MiniError('type')
        z=(x.v is y.v) if isinstance(x,_Ref) else x==y
        return not z if op=='!=' else z
    raise MiniError('parse')

def _match(p,v,b):
    if p[0]=='_': return True
    if p[0]=='bind': b[p[1]]=v; return True
    if p[0]=='lit':
        x=p[1]; return type(x) is type(v) and x==v
    if p[0]=='recordpat':
        if not isinstance(v,dict): return False
        for n,q in p[1]:
            if n not in v or not _match(q,v[n],b): return False
        return True
    return False

def _convert(v):
    if isinstance(v,dict): return {k:_convert(x) for k,x in v.items()}
    if isinstance(v,_Closure): return '<fn>'
    if isinstance(v,_Ref): return '<ref>'
    return v

def run(source):
    p=_Parser(source); tree=p.expr()
    if p.k() != 'EOF': raise MiniError('parse')
    return _convert(_ev(tree,_Env()))
