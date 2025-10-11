claude_4_5_sonnet_models = [   # Sonnet 4.5
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    }
]

claude_4_opus_models = [   # Opus 4
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "us.anthropic.claude-opus-4-20250514-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-4-opus-20250514-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-4-opus-20250514-v1:0"
    }
]

claude_4_sonnet_models = [   # Sonnet 4
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-4-sonnet-20250219-v1:0"
    }
]

claude_3_7_sonnet_models = [   # Sonnet 3.7
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    }
]

claude_3_5_sonnet_v1_models = [   # Sonnet 3.5 V1
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    }
]

claude_3_5_sonnet_v2_models = [   # Sonnet 3.5 V2
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    }
]

claude_3_5_haiku_models = [   # Haiku 3.5 
    {
        "bedrock_region": "us-west-2", # Oregon
        "model_type": "claude",
        "model_id": "anthropic.claude-3-5-haiku-20241022-v1:0"
    },
    {
        "bedrock_region": "us-east-1", # N.Virginia
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    },
    {
        "bedrock_region": "us-east-2", # Ohio
        "model_type": "claude",
        "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    }
]

def get_model_info(model_name):
    models = []

    if model_name == "Claude 3.7 Sonnet":
        models = claude_3_7_sonnet_models
    elif model_name == "Claude 3.5 Sonnet":
        models = claude_3_5_sonnet_v2_models
    elif model_name == "Claude 3.5 Haiku":
        models = claude_3_5_haiku_models
    elif model_name == "Claude 4 Opus":
        models = claude_4_opus_models
    elif model_name == "Claude 4 Sonnet":
        models = claude_4_sonnet_models
    elif model_name == "Claude 4.5 Sonnet":
        models = claude_4_5_sonnet_models
    
    return models

STOP_SEQUENCE_CLAUDE = "\n\nHuman:" 

def get_stop_sequence(model_name):
    return STOP_SEQUENCE_CLAUDE
    