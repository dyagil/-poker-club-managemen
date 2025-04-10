#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive solution for the super agent filtering issue in the payment system
"""

import re

def fix_super_agent_filter():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Helper function to add at the top of the file
    helper_function = """
# Helper function to find agents for a super agent
def find_agents_for_super_agent(game_stats, super_agent_name, super_agent_entities):
    """Function to find agents associated with a specific super agent"""
    print(f"DEBUG: Finding agents for super agent: {super_agent_name}")
    print(f"DEBUG: Super agent entities: {super_agent_entities}")
    
    if not game_stats:
        print("DEBUG: No game stats data available")
        return set()
    
    # List of agents found
    found_agents = set()
    
    # Possible super agent names in the data
    possible_super_agent_names = set()
    
    # Agent to super agent mapping from data
    agent_to_super_agent = {}
    
    # 1. Collect all super agent names and agent-super agent mapping from data
    for game in game_stats:
        if not isinstance(game, dict):
            continue
            
        agent_name = str(game.get('שם אייגנט', '')).strip() if game.get('שם אייגנט') is not None else ''
        super_agent_in_game = str(game.get('שם סופר אייגנט', '')).strip() if game.get('שם סופר אייגנט') is not None else ''
        
        if super_agent_in_game:
            possible_super_agent_names.add(super_agent_in_game)
            
            if agent_name:
                agent_to_super_agent[agent_name] = super_agent_in_game
    
    print(f"DEBUG: All super agent names found in data: {possible_super_agent_names}")
    print(f"DEBUG: Agent to Super Agent mapping: {agent_to_super_agent}")
    
    # Is the logged-in super agent name exactly in the list?
    exact_name_match = False
    if super_agent_name in possible_super_agent_names:
        exact_name_match = True
        print(f"DEBUG: Found exact match for super agent name: {super_agent_name}")
    
    # 2. Check by entities - first priority
    if super_agent_entities:
        print(f"DEBUG: Checking by entities: {super_agent_entities}")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            for entity in super_agent_entities:
                entity_str = str(entity).strip()
                sa_in_game_str = str(sa_in_game).strip()
                
                # Check exact or partial match
                if entity_str == sa_in_game_str or entity_str in sa_in_game_str or sa_in_game_str in entity_str:
                    found_agents.add(agent_name)
                    print(f"DEBUG: Added agent '{agent_name}' based on entity match: '{entity_str}' <-> '{sa_in_game_str}'")
    
    # 3. Check by super agent name - second priority
    if not found_agents and super_agent_name:
        print(f"DEBUG: No agents found by entities, checking by super agent name: {super_agent_name}")
        super_agent_name_str = str(super_agent_name).strip()
        
        for agent_name, sa_in_game in agent_to_super_agent.items():
            sa_in_game_str = str(sa_in_game).strip()
            
            # Check exact or partial match
            if sa_in_game_str == super_agent_name_str or sa_in_game_str in super_agent_name_str or super_agent_name_str in sa_in_game_str:
                found_agents.add(agent_name)
                print(f"DEBUG: Added agent '{agent_name}' based on name match: '{super_agent_name_str}' <-> '{sa_in_game_str}'")
    
    # 4. Check exact match - if found earlier
    if not found_agents and exact_name_match:
        print(f"DEBUG: Trying exact name match for: {super_agent_name}")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            if str(sa_in_game).strip() == str(super_agent_name).strip():
                found_agents.add(agent_name)
                print(f"DEBUG: Added agent '{agent_name}' based on exact name match")
    
    # 5. Additional check - if super agent name contains entity or vice versa
    if not found_agents and super_agent_entities:
        print(f"DEBUG: Trying partial entity matches")
        for agent_name, sa_in_game in agent_to_super_agent.items():
            sa_game_lower = str(sa_in_game).lower().strip()
            
            for entity in super_agent_entities:
                entity_lower = str(entity).lower().strip()
                
                # Check more partial overlaps (case insensitive)
                if (entity_lower and sa_game_lower and 
                   (entity_lower in sa_game_lower or sa_game_lower in entity_lower or
                    any(word in sa_game_lower for word in entity_lower.split()) or
                    any(word in entity_lower for word in sa_game_lower.split()))):
                    found_agents.add(agent_name)
                    print(f"DEBUG: Added agent '{agent_name}' based on partial entity match: '{entity}' <-> '{sa_in_game}'")
    
    print(f"DEBUG: Total agents found for super agent: {len(found_agents)}")
    return found_agents
"""
    
    # Replace existing agents function
    agents_route = """@app.route('/agents', methods=['GET'])
@login_required
def agents():
    """Display agents with filtering for super-agent"""
    # Load data
    excel_data = read_excel_data()
    
    # List of all agents
    agents_list = excel_data.get('agents', [])
    
    # User role and entities
    user_role = session.get('role', '')
    user_entities = session.get('entities', [])
    user_name = session.get('name', '')
    super_agent_name = user_name if user_role == 'super_agent' else None
    
    print(f"DEBUG: User role: {user_role}")
    print(f"DEBUG: Super Agent Name: {super_agent_name}")
    print(f"DEBUG: User entities: {user_entities}")
    
    # If not a super agent, show all agents
    if user_role != 'super_agent':
        return render_template('agents.html', agents=agents_list, active_page='agents')
    
    # For super agent, find their associated agents
    game_stats = excel_data.get('game_stats', [])
    super_agent_agents = find_agents_for_super_agent(game_stats, super_agent_name, user_entities)
    
    # If agents found, show only those
    if super_agent_agents:
        super_agent_agents_list = [a for a in agents_list if a in super_agent_agents]
        print(f"DEBUG: Showing filtered agents: {super_agent_agents_list}")
        return render_template('agents.html', agents=super_agent_agents_list, active_page='agents')
    else:
        print(f"DEBUG: No agents found for this super agent specifically, showing all agents")
        return render_template('agents.html', agents=agents_list, active_page='agents')"""
    
    # Add helper function (if it doesn't exist)
    if "def find_agents_for_super_agent" not in content:
        content = content.replace("app = Flask(__name__)", "app = Flask(__name__)" + helper_function)
    
    # Replace existing function
    pattern = r"@app\.route\('/agents'.*?def agents\(\):.*?active_page='agents'\)"
    updated_content = re.sub(pattern, agents_route, content, flags=re.DOTALL)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Filter function update completed successfully!")

if __name__ == "__main__":
    fix_super_agent_filter()
