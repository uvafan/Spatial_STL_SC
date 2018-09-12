'''
Timothy Davison, Eli Lifland
9/11/18
Preliminary Model Checking Functions
'''
import sc_lib

'''
Functions assume the trace contains only the necessary node data;
ie, that it does not require further processing, and is passed in the 
form of a pandas dataframe with all rows being relevant. Later functions should
use these as a base on which to build a requirement parse/ node retrieval function.

Note that always/everywhere and eventually/somewhere share the same code, but assume 
different dataframes are passed in (containing temporal versus spatial data, respectively).
'''

def sstl_parse_evaluate(requirement):
    # Interpret text of requirement, convert to SSTL logic
    # Break up logic into basic predicates (if compound/complex)
    # For each predicate, extract the desired dataframe from the SC_Lib graph
        # Pass the desired dataframe into the necessary functions below
        # Evaluate their satisfaction (by t/f, robust, percent, integral)
    # Combine predicate satisfaction degrees
    # Return desired format of satisfaction measurement
    return;

'''
Pass in target nodes in an area (graph or set form), iterate over full time frame.
May be useful to write another function which allows time frame specification within the 
function itself (as it is currently assumed all times are relevant within the passed dataframe)

** Just added -- sstl_integral with timesets (pass in a set of the target times)
'''
def sstl_integral(area, target, operator, threshold):
    if type(area) == sc_lib.graph:
        nodes = area.nodes
    else:
        nodes = area
    integral = 0.0
    
    if operator == "<=":
        for node in nodes:
            for index, row in node.data.iterrows():
                if float(row[target]) > threshold:
                   integral += float(row[target]) - threshold   
        return integral

    if operator == ">=":
        for node in nodes:
            for index, row in node.data.iterrows():
                if float(row[target]) < threshold:
                   integral += threshold - float(row[target])       
        return integral
    
    if operator == "<":
        for node in nodes:
            for index, row in node.data.iterrows():
                if float(row[target]) >= threshold:
                   integral += float(row[target]) - threshold   
        return integral

    if operator == ">":
        for node in nodes:
            for index, row in node.data.iterrows():
                if float(row[target]) < threshold:
                   integral += threshold - float(row[target])       
        return integral

    if operator == "==":
        for node in nodes:
            for index, row in node.data.iterrows():
                if float(row[target]) < threshold:
                   integral += abs(threshold - float(row[target]))       
        return integral
    
    
def sstl_integral_timeset(area, timeset, operator, threshold):
    if type(area) == sc_lib.graph:
        nodes = area.nodes
    else:
        nodes = area
    integral = 0.0
    
    if operator == "<=":
        for node in nodes:
            for time in timeset:
                for index, row in node.data[timeset].iterrows():
                    if float(row[time]) > threshold:
                       integral += float(row[time]) - threshold   
        return integral
    
    if operator == ">=":
        for node in nodes:
            for time in timeset:
                for index, row in node.data[time].iterrows():
                    if float(row[time]) < threshold:
                       integral += threshold - float(row[time])       
        return integral
    
    if operator == "<":
        for node in nodes:
            for time in timeset:
                for index, row in node.data[timeset].iterrows():
                    if float(row[time]) >= threshold:
                       integral += float(row[time]) - threshold   
        return integral

    if operator == ">=":
        for node in nodes:
            for time in timeset:
                for index, row in node.data[time].iterrows():
                    if float(row[time]) <= threshold:
                       integral += threshold - float(row[time])       
        return integral

    if operator == "==":
        for node in nodes:
            for time in timeset:
                for index, row in node.data[time].iterrows():
                    if float(row[time]) != threshold:
                       integral += abs(threshold - float(row[time]))       
        return integral
'''
Percent satisfaction: gives a float value of satisfied/not satisfied requirements based on 
each node's true or false value. Eventually and Somewhere unfinished - what would it mean for 
an "eventually" or "somewhere" requirement to be some percent satisfied?
'''
def percent_eventually(trace, target, operator, threshold):
    return;

def percent_somewhere(trace, target, operator, threshold):
    return;

def percent_always(trace, target, operator, threshold):
    s_counter = 0.0
    ns_counter = 0.0
    if operator == "<=":
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    
    if operator == ">=":
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "<":
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    
    if operator == ">":
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "==":
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "!=":
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    

def percent_everywhere(trace, target, operator, threshold):
    s_counter = 0.0
    ns_counter = 0.0
    if operator == "<=":
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    
    if operator == ">=":
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "<":
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    
    if operator == ">":
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "==":
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))

    if operator == "!=":
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                ns_counter +=1 
            else:
                s_counter += 1
        return (s_counter/(s_counter+ns_counter))
    

'''
True/False, Robustness model checking.
Assumes you pass a trace (pandas DF) of nodes over already decided relevant times and areas.
Possible room for optimization -- give each operator its own function?
'''
def tf_always(trace, target, operator, threshold):
    if operator == '<=': 
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return False
        return True;
    
    elif operator == '>=': 
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return False
        return True;
    
    elif operator == '<': 
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return False
        return True;
    
    elif operator == '>': 
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return False
        return True;

    elif operator == '==': 
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return False
        return True;
    
    elif operator == '!=': 
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return False
        return True;

def tf_eventually(trace, target, operator, threshold):
    if operator == '<=':
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return True
        return False;

    if operator == '>=':
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return True
        return False;
    
    if operator == '<':
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return True
        return False;
    
    if operator == '>':
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return True
        return False;
    
    if operator == '==':
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return True
        return False;
    
    if operator == '!=':
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return True
        return False;

'''
Assumes you pass a trace (pandas DF) of nodes over relevant area.
'''
def tf_everywhere(trace, target, operator, threshold):
    if operator == '<=': 
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return False
        return True;
    
    elif operator == '>=': 
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return False
        return True;
    
    elif operator == '<': 
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return False
        return True;
    
    elif operator == '>': 
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return False
        return True;

    elif operator == '==': 
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return False
        return True;
    
    elif operator == '!=': 
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return False
        return True;


def tf_somewhere(trace, target, operator, threshold):
    if operator == '<=':
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return True
        return False;

    if operator == '>=':
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return True
        return False;
    
    if operator == '<':
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return True
        return False;
    
    if operator == '>':
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return True
        return False;
    
    if operator == '==':
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return True
        return False;
    
    if operator == '!=':
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return True
        return False;


'''
Same as above, but returns robustness (defined as max(|violating values|)) instead of a t/f value.
'''
def robust_always(trace, target, operator, threshold):
    if operator == '>=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        min_violation = min(violations)
        return min_violation;
    
    if operator == '<=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        max_violation = min(violations)
        return max_violation;
    
    if operator == '>':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        min_violation = min(violations)
        return min_violation;
    
    if operator == '<':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        max_violation = min(violations)
        return max_violation;

    if operator == '==':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        return violations;

    if operator == '!=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        return violations;


def robust_eventually(trace, target, operator, threshold):
    if operator == '<=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return True
            else:
                violations.add(float(row[target]))
        max_violation = max(violations)
        return max_violation;

    if operator == '>=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return True
            else:
                violations.add(float(row[target]))
        min_violation = max(violations)
        return min_violation;
    
    if operator == '<':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return True
            else:
                violations.add(float(row[target]))
        max_violation = max(violations)
        return max_violation;
    
    if operator == '>':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return True
            else:
                violations.add(float(row[target]))
        min_violation = max(violations)
        return min_violation;
    
    if operator == '==':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return True
            else:
                violations.add(float(row[target]))
        return violations;

    if operator == '!=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return True
            else:
                violations.add(float(row[target]))
        return violations;

def robust_everywhere(trace, target, operator, threshold):
    if operator == '>=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        min_violation = min(violations)
        return min_violation;
    
    if operator == '<=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        max_violation = min(violations)
        return max_violation;
    
    if operator == '>':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        min_violation = min(violations)
        return min_violation;
    
    if operator == '<':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        max_violation = min(violations)
        return max_violation;

    if operator == '==':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        return violations;

    if operator == '!=':
        violations = set([])
        tf = True
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                violations.add(float(row[target]))
                tf = False
        if tf:
            return True
        return violations;

def robust_somewhere(trace, target, operator, threshold):
    if operator == '<=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) <= threshold:
                return True
            else:
                violations.add(float(row[target]))
        max_violation = max(violations)
        return max_violation;

    if operator == '>=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) >= threshold:
                return True
            else:
                violations.add(float(row[target]))
        min_violation = max(violations)
        return min_violation;
    
    if operator == '<':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) < threshold:
                return True
            else:
                violations.add(float(row[target]))
        max_violation = max(violations)
        return max_violation;
    
    if operator == '>':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) > threshold:
                return True
            else:
                violations.add(float(row[target]))
        min_violation = max(violations)
        return min_violation;
    
    if operator == '==':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) == threshold:
                return True
            else:
                violations.add(float(row[target]))
        return violations;

    if operator == '!=':
        violations = set([])
        for index, row in trace.iterrows():
            if float(row[target]) != threshold:
                return True
            else:
                violations.add(float(row[target]))
        return violations;
