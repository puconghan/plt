# -----------------------------------------------------------------------------
# parsingrules.py
# This file contains the rules that are used for parsing
# and generation of the abstract syntax tree by the yacc module of PLY.
# -----------------------------------------------------------------------------
# Authors ->
#	This file was originally written by Hareesh.
#		Robert wrote the grammar for binary operations.
#		David wrote the grammar for conditionals.
#		Victoria wrote the grammar for custom functions.
#		All error handling was taken care of by Pucong.
#
#	The author names are listed above each subsection
# -----------------------------------------------------------------------------

import trowelglobals as tgl
from lexingrules import *

##~~~~~ Section author 1: Hareesh
#-----------------------------------------------------
start = 'STATEMENT'

def p_statement(p):
	'''
	STATEMENT : ROOTEXPRESSION
			| DECLARATION
			| ASSIGNMENT
			| CONDITIONAL
			| FORSTATEMENT
			| CUSTOM
	'''
	p[0] = [['indentlevel',tgl.indentlevel],p[1]]
		
def p_error(p):
	tgl.returnError("Syntax Error", "Syntax error at '%s'" % p.value, False)
	
#---------------------

##Parsing expressions
def p_rootexpression(p):
	'''
	ROOTEXPRESSION : EXPRESSION
				   | FUNCTION
	'''
	if p[1][0] == 'functioncall':
		p[1] = ['expression',p[1]]
	p[0] = p[1]

def p_expression_1(p):
	'EXPRESSION	: IDENTIFIER'
	if tgl.funclist.get(p[1][1]) != None:
		p[0] = ['expression',['functioncall',p[1],'arguments',[]]]
	else:
		p[0] = ['expression',p[1]]
def p_expression_2(p):
	'''
	EXPRESSION :	VALUE
			| LIST
			| LEFTPAREN FUNCTION RIGHTPAREN
			| BINOP
			| LEFTPAREN BINOP RIGHTPAREN
			| RELOP
			| LEFTPAREN RELOP RIGHTPAREN
	'''
	if len(p) == 2:
		p[0] = ['expression',p[1]]
	else:
		p[0] = ['expression',p[2]]

#---------------------

##Parsing assignments
def p_assignment(p):
	'ASSIGNMENT : IDENTIFIER IS ROOTEXPRESSION'
	p[0] = ['assignment', p[1], p[3]]

def p_identifier(p):
	'''
	IDENTIFIER :	UNKNOWNWORD
			| LOGICAL
	'''
	if tgl.funclist.get(p[1]) != None:
		p[0] = ['functionname',p[1]]
	elif tgl.varlist[tgl.indentlevel].get(p[1]) != None:
		p[0] = ['variable',p[1]]
	else:
		p[0] = ['insertword',p[1]]
		
#---------------------

##Parsing functions
def p_function(p):
	'FUNCTION : IDENTIFIER EXPRESSIONSET'
	p[0] = ['functioncall',p[1],'arguments',p[2]]

def p_expressionset(p):
	'''
	EXPRESSIONSET : EXPRESSIONSET EXPRESSION
				  | EXPRESSION
	'''
	if len(p) == 3:
		p[0] = p[1] + [p[2]]
	else:
		p[0] = [p[1]]
	
#---------------------

##Parsing for
def p_for(p):
	'FORSTATEMENT : FOR UNKNOWNWORD UNKNOWNWORD ROOTEXPRESSION COLON'
	if p[3] != 'in':
		#throw error - systax of for should be
		pass
	elif (tgl.funclist.get(p[3]) != None) or (tgl.varlist[tgl.indentlevel].get(p[3]) != None):
		#Error. Variable already defined.		
		pass
	else:
		tgl.varlist[tgl.indentlevel][p[2]] = 'list'
		p[0] = ['forstatement',['variable',p[2]],p[4]]
		
#def p_lambdavar(p):		
#	'LAMBDAVAR: LEFTPAREN DATATYPE UNKNOWNWORD RIGHTPAREN'
#	p[0] = ['lambdavar',[p[2],p[3]]]


#---------------------

##Parsing constants and lists
def p_value(p):
	'''
	VALUE : _URLVAL
		  | _TEXTVAL
		  | _NUMVAL
	'''
	p[0] = p[1]
	
def p_urlval(p):
	'_URLVAL : URLVAL'
	p[0] = ['value',['url',p[1][1:-1]]]
	
def p_textval(p):
	'_TEXTVAL : TEXTVAL'
	p[0] = ['value',['text',p[1][1:-1]]]
	
def p_numval(p):
	'_NUMVAL : NUMVAL'
	p[0] = ['value',['number',int(p[1])]]
	
def p_valueset(p):
	'''
	LISTSET	: EXPRESSION COMMA LISTSET
			| EXPRESSION
	'''
	#Add expression here
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]

def p_valuelist(p):
	'LIST : LEFTSQUAREBRACKET LISTSET RIGHTSQUAREBRACKET'
	list = []
	for item in p[2]:
		#list = list + [item[1]]
		list = list + [item]
	p[0] = ['list',list]

#---------------------

##Parsing declarations	
def p_declaration(p):
	'DECLARATION : DATATYPE DECLARATIONSET'
	p[0] = ['declaration',p[1],p[2]]
	for varobj in p[2]:
		if (tgl.reservedlist.get(varobj[0]) == None) and (tgl.funclist.get(varobj[0]) == None) and (tgl.varlist[tgl.indentlevel].get(varobj[0]) == None):
			tgl.varlist[tgl.indentlevel][varobj[0]] = p[1][1]
	
def p_datatype(p):
	'''
	DATATYPE : URL
			 | TEXT
			 | NUMBER
			 | URLLIST
			 | TEXTLIST
			 | NUMLIST
	'''
	p[0] = ['datatype',p[1]]
	
def p_declarationset(p):
	'''
	DECLARATIONSET	: DECLAREDVAR COMMA DECLARATIONSET
					| DECLAREDVAR
	'''
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]
	
def p_declarationassign(p):
	'''
	DECLAREDVAR	: UNKNOWNWORD IS ROOTEXPRESSION
				| UNKNOWNWORD
	'''
	if (tgl.funclist.get(p[1]) != None) or (tgl.varlist[tgl.indentlevel].get(p[1]) != None):
		#Error. Variable already defined.		
		pass
	elif len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1],p[3]]

#-----------------------------------------------------
##~~~~~ Section author 2: Robert

precedence = (
    ('left','PLUS','MINUS'),
    ('left','MULTIPLY','DIVISION'),
    ('right','UMINUS'),
    )

def p_expression_uminus(p):
    'EXPRESSION : MINUS EXPRESSION %prec UMINUS'
    if (p[2][1][0] == "value"):
    	p[2][1][1][1] = -p[2][1][1][1]
    else:
    	p[2][1][1] = "-" + p[2][1][1]
    p[0] = p[2]


##Parsing Binary Operations

def p_binop(p):
	'''BINOP : EXPRESSION PLUS EXPRESSION
			| EXPRESSION MINUS EXPRESSION
			| EXPRESSION MULTIPLY EXPRESSION
			| EXPRESSION DIVISION EXPRESSION'''
	if p[2] == "+":
		p[2] = "plus"
	if p[2] == "-":
		p[2] = "minus"
	if p[2] == "*":
		p[2] = "multiply"
	if p[2] == "/":
		p[2] = "divide"

	p[0] = ['functioncall', ['functionname',p[2]],'arguments', [p[1], p[3]]]

#-----------------------------------------------------
##~~~~~ Section author 3: David

##Parsing Relational Operations
def p_relop(p):
	'''
	RELOP :	EXPRESSION GREATER EXPRESSION
		| EXPRESSION LESS EXPRESSION
		| EXPRESSION EQUAL EXPRESSION
		| EXPRESSION NOTEQUAL EXPRESSION
	'''
	if p[2] == ">": p[2] = "greater"
	elif p[2] == "<": p[2] = "less"
	elif p[2] == "==": p[2] = "equal"
	elif p[2] == '=/=': p[2] = "notequal"
	else: raise Exception('Illegal relational operator')

	p[0] = ['functioncall', ['functionname', p[2]], 'arguments', [p[1], p[3]]]
	
#---------------------

##Parsing conditionals
def p_conditional(p):
	'CONDITIONAL : CONTROL BOOLEAN_LIST COLON'
	p[0] = ['conditional', p[1], p[2]]

def p_control(p):
	'''
	CONTROL :	IF
			| ELSEIF
			| ELSE
	'''
	p[0] = ['control', p[1]]

def p_boolean_list(p):
	'''
	BOOLEAN_LIST :	BOOLEAN_LIST LOGICAL BOOLEAN
			| BOOLEAN
	'''
	p[0] = ['boolean_list', p[1:]]

def p_boolean(p):
	'''
	BOOLEAN :	LEFTPAREN BOOLEAN_LIST RIGHTPAREN
			| NOT BOOLEAN
			| EXPRESSION
			| EMPTY
	'''
	p[0] = p[1:]

def p_logical(p):
	'''
	LOGICAL :	AND
			| OR
			| NOT
	'''
	p[0] = p[1]

#----------------------------------------------------
##~~~~~ Section author 4: Victoria

##Parsing custom functions
def p_custom_function(p):
	'CUSTOM : DEFINE UNKNOWNWORD CUSTOMARGS COLON'
	p[0] = ['custom',p[2],p[3]]

def p_customargs(p):
	'''
	CUSTOMARGS : CUSTOMARGS LEFTPAREN DATATYPE UNKNOWNWORD RIGHTPAREN
			   | CUSTOMARGS UNKNOWNWORD
			   | EMPTY
	'''
	if p[1] is None:
		p[0] = p[2:]
	else:
		p[0] = p[1] + [x for x in p[2:] if x is not '(' and x is not ')']

def p_return(p):

	'CUSTOM : RETURN ROOTEXPRESSION'
	p[0] = ['custom', 'return', p[2]]
	
#----------------------------------------------------

##Parsing comments
def p_comment(p):
	'''
	STATEMENT : COMMENT
	'''
	pass

##Empty handle
def p_empty(p):
	'EMPTY :'
	pass