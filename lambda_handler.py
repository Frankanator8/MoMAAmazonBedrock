import json

def lambda_handler(event, context):
    
    """
    Lambda function to handle healthcare cost calculations for Bedrock Agent
    """
 
    print(f"Received event: {json.dumps(event)}")
    
    # Extract the action group, API path, and parameters
    agent = event.get('agent', {})
    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = event.get('parameters', [])
    content = event.get("requestBody", {}).get("content", {}).get("application/json", []).get("properties", [])
    # Convert parameters list to dictionary for easier access
    
    try:  
        params_dict = {param['name']: param['value'] for param in content}
        # Route to appropriate function based on API path
        if api_path == '/calculateOutOfPocketCost':
            response_body = calculate_out_of_pocket_cost(params_dict)
        elif api_path == '/comparePrices':
            response_body = compare_hospital_prices(params_dict)
        elif api_path == '/calculateCoinsurance':
            response_body = calculate_coinsurance(params_dict)
        else:
            response_body = {
                'error': f'Unknown API path: {api_path}'
            }

    except Exception as e:
        response_body = {
            'error': f'Error processing request: {e}\n{agent}\n{content}\n{type(content)}\n{parameters}'
        }
    
    # Format response for Bedrock Agent
    action_response = {
        'actionGroup': action_group,
        'apiPath': api_path,
        'httpMethod': event.get('httpMethod', 'POST'),
        'httpStatusCode': 200,
        'responseBody': {
            'application/json': {
                'body': json.dumps(response_body)
            }
        }
    }
    
    return {
        'messageVersion': '1.0',
        'response': action_response
    }


def calculate_out_of_pocket_cost(params):
    """
    Calculate patient's out-of-pocket cost based on deductible and coinsurance
    
    Parameters:
    - procedure_cost: Total cost of the procedure
    - deductible: Annual deductible amount
    - deductible_paid: Amount already paid toward deductible
    - coinsurance_percent: Coinsurance percentage (e.g., 20 for 20%)
    """
    try:
        procedure_cost = float(params.get('procedure_cost', 0))
        deductible = float(params.get('deductible', 0))
        deductible_paid = float(params.get('deductible_paid', 0))
        coinsurance_percent = float(params.get('coinsurance_percent', 20))
        
        # Calculate remaining deductible
        remaining_deductible = max(0, deductible - deductible_paid)
        
        # Calculate out-of-pocket cost
        if procedure_cost <= remaining_deductible:
            # Patient pays entire cost (still meeting deductible)
            out_of_pocket = procedure_cost
            deductible_portion = procedure_cost
            coinsurance_portion = 0
            explanation = f"You will pay the full ${procedure_cost:.2f} which goes toward your remaining ${remaining_deductible:.2f} deductible."
        else:
            # Patient pays remaining deductible + coinsurance on the rest
            deductible_portion = remaining_deductible
            amount_after_deductible = procedure_cost - remaining_deductible
            coinsurance_portion = amount_after_deductible * (coinsurance_percent / 100)
            out_of_pocket = deductible_portion + coinsurance_portion
            
            if remaining_deductible > 0:
                explanation = f"You will pay ${deductible_portion:.2f} toward your deductible, plus {coinsurance_percent}% coinsurance (${coinsurance_portion:.2f}) on the remaining ${amount_after_deductible:.2f}, for a total of ${out_of_pocket:.2f}."
            else:
                explanation = f"Your deductible is met. You will pay {coinsurance_percent}% coinsurance (${coinsurance_portion:.2f}) on the ${procedure_cost:.2f} procedure cost."
        
        return {
            'success': True,
            'out_of_pocket_cost': round(out_of_pocket, 2),
            'deductible_portion': round(deductible_portion, 2),
            'coinsurance_portion': round(coinsurance_portion, 2),
            'explanation': explanation
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def compare_hospital_prices(params):
    """
    Compare prices across multiple hospitals
    
    Parameters:
    - hospital_prices: JSON string of hospital names and prices
      Example: '{"Rhode Island Hospital": 1200, "Miriam Hospital": 950, "Butler Hospital": 1100}'
    """
    try:
        hospital_prices_str = params.get('hospital_prices', '{}')
        hospital_prices = json.loads(hospital_prices_str)
        
        if not hospital_prices:
            return {
                'success': False,
                'error': 'No hospital prices provided'
            }
        
        # Find min and max prices
        min_hospital = min(hospital_prices.items(), key=lambda x: x[1])
        max_hospital = max(hospital_prices.items(), key=lambda x: x[1])
        
        # Calculate savings
        savings = max_hospital[1] - min_hospital[1]
        savings_percent = (savings / max_hospital[1]) * 100
        
        # Sort hospitals by price
        sorted_prices = sorted(hospital_prices.items(), key=lambda x: x[1])
        
        comparison_text = "\n".join([
            f"{hospital}: ${price:.2f}" 
            for hospital, price in sorted_prices
        ])
        
        return {
            'success': True,
            'lowest_price_hospital': min_hospital[0],
            'lowest_price': round(min_hospital[1], 2),
            'highest_price_hospital': max_hospital[0],
            'highest_price': round(max_hospital[1], 2),
            'potential_savings': round(savings, 2),
            'savings_percent': round(savings_percent, 1),
            'comparison': comparison_text,
            'explanation': f"The lowest price is ${min_hospital[1]:.2f} at {min_hospital[0]}. You could save ${savings:.2f} ({savings_percent:.1f}%) compared to the highest price of ${max_hospital[1]:.2f} at {max_hospital[0]}."
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def calculate_coinsurance(params):
    """
    Calculate coinsurance amount
    
    Parameters:
    - amount: Amount to calculate coinsurance on
    - coinsurance_percent: Coinsurance percentage
    """
    try:
        amount = float(params.get('amount', 0))
        coinsurance_percent = float(params.get('coinsurance_percent', 20))
        
        coinsurance_amount = amount * (coinsurance_percent / 100)
        
        return {
            'success': True,
            'coinsurance_amount': round(coinsurance_amount, 2),
            'explanation': f"{coinsurance_percent}% of ${amount:.2f} is ${coinsurance_amount:.2f}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
