# _models_data.py - Model data for LSDAI widgets
# Contains lists of popular models, VAEs, LoRAs, and ControlNet models

# Stable Diffusion Models
model_list = {
    "Popular SD 1.5 Models": [
        "Realistic Vision V6.0 B1",
        "DreamShaper",
        "Deliberate v2",
        "ChilloutMix",
        "AbyssOrangeMix3 (AOM3)",
        "Anything V4.5",
        "Rev Animated",
        "MajicMix Realistic",
        "Perfect World",
        "Epic Realism"
    ],
    "Popular SDXL Models": [
        "SDXL Base 1.0",
        "Juggernaut XL",
        "RealVisXL V4.0",
        "DreamShaper XL",
        "Crystal Clear XL",
        "Copax TimeLessXL",
        "Animagine XL 3.1",
        "Pony Diffusion V6 XL",
        "RealCartoon-Pixar",
        "SDXL Lightning"
    ],
    "Anime/Cartoon Models": [
        "Anything V5",
        "CounterfeitXL",
        "MeinaMix",
        "Perfect World",
        "AnythingXL",
        "Animagine XL",
        "Waifu Diffusion",
        "NovelAI Animefull",
        "CuteYukiMix",
        "GhostMix"
    ],
    "Artistic Models": [
        "OpenJourney",
        "Midjourney V4 Diffusion", 
        "Analog Diffusion",
        "Vintedois Diffusion",
        "Protogen Infinity",
        "Epic Diffusion",
        "Fantasy.ai",
        "AlbedoBase XL",
        "Juggernaut Aftermath",
        "Crystal Clear XL"
    ],
    "Realistic Models": [
        "Realistic Vision V6.0",
        "Epic Realism",
        "AbsoluteReality",
        "epiCRealism",
        "Beautiful Realistic Asians",
        "RealVisXL V4.0",
        "Cyberrealistic",
        "MajicMix Realistic",
        "Perfect World",
        "PhotoReal"
    ]
}

# VAE Models
vae_list = {
    "Popular VAEs": [
        "vae-ft-mse-840000-ema-pruned",
        "sd-vae-ft-ema-original",
        "sd-vae-ft-mse-original",
        "kl-f8-anime2",
        "blessed2.vae",
        "ClearVAE_V2.3",
        "orangemix.vae",
        "pastel-waifu-diffusion.vae",
        "anything-v4.0.vae",
        "sdxl_vae"
    ],
    "Anime VAEs": [
        "kl-f8-anime2",
        "blessed2.vae",
        "orangemix.vae",
        "pastel-waifu-diffusion.vae",
        "anything-v4.0.vae",
        "novel-ai-anime-vae",
        "waifuDiffusion.vae"
    ],
    "Realistic VAEs": [
        "vae-ft-mse-840000-ema-pruned",
        "sd-vae-ft-ema-original",
        "ClearVAE_V2.3",
        "realistic.vae"
    ],
    "SDXL VAEs": [
        "sdxl_vae",
        "sdxl-vae-fp16-fix",
        "fixedvae"
    ]
}

# LoRA Models
lora_list = {
    "Character LoRAs": [
        "Genshin Impact Characters",
        "Anime Characters Pack",
        "Celebrity Faces",
        "Game Characters",
        "Disney Characters",
        "Marvel Characters",
        "Popular Waifus",
        "VTuber Pack"
    ],
    "Style LoRAs": [
        "Pixel Art Style",
        "Oil Painting Style",
        "Watercolor Style",
        "Sketch Style",
        "Anime Style Enhancer",
        "Photorealistic Enhancer",
        "Studio Ghibli Style",
        "Comic Book Style",
        "Cyberpunk Style",
        "Fantasy Art Style"
    ],
    "Concept LoRAs": [
        "Better Hands",
        "Detail Tweaker",
        "Add More Details",
        "Lighting Enhancer",
        "Background Enhancer",
        "Face Enhancer",
        "Eye Detail",
        "Hair Detail",
        "Clothing Detail",
        "Architecture Helper"
    ],
    "Clothing LoRAs": [
        "Modern Fashion",
        "Historical Clothing",
        "Fantasy Outfits",
        "School Uniforms",
        "Cosplay Outfits",
        "Military Uniforms",
        "Traditional Clothing",
        "Futuristic Clothing"
    ],
    "Pose LoRAs": [
        "Dynamic Poses",
        "Sitting Poses",
        "Standing Poses",
        "Action Poses",
        "Portrait Poses",
        "Group Poses",
        "Hand Poses",
        "Dancing Poses"
    ]
}

# ControlNet Models
controlnet_list = {
    "SD 1.5 ControlNet": [
        "control_v11p_sd15_canny",
        "control_v11p_sd15_depth",
        "control_v11p_sd15_openpose",
        "control_v11p_sd15_scribble",
        "control_v11p_sd15_seg",
        "control_v11p_sd15_softedge",
        "control_v11p_sd15_normalbae",
        "control_v11p_sd15_lineart",
        "control_v11p_sd15_lineart_anime",
        "control_v11p_sd15_mlsd",
        "control_v11p_sd15_inpaint",
        "control_v11e_sd15_shuffle",
        "control_v11e_sd15_ip2p",
        "control_v11f1e_sd15_tile"
    ],
    "SDXL ControlNet": [
        "control-lora-canny-rank256",
        "control-lora-depth-rank256", 
        "control-lora-recolor-rank256",
        "control-lora-sketch-rank256",
        "controlnet-canny-sdxl-1.0",
        "controlnet-depth-sdxl-1.0",
        "controlnet-openpose-sdxl-1.0",
        "sai-controlnet-sdxl-canny",
        "sai-controlnet-sdxl-depth",
        "diffusers-controlnet-canny-sdxl",
        "diffusers-controlnet-depth-sdxl"
    ],
    "Specialized ControlNet": [
        "control_v11p_sd15_qrcode_monster",
        "control_v11u_sd15_tile",
        "control_v1p_sd15_brightness",
        "control_v11p_sd15_s2_lineart_anime",
        "control_v11p_sd15_anime",
        "t2iadapter_canny_sd15v2",
        "t2iadapter_depth_sd15v2",
        "t2iadapter_sketch_sd15v2",
        "t2iadapter_openpose_sd15v2"
    ]
}

# Extension Lists
extension_list = {
    "Essential Extensions": [
        "sd-webui-controlnet",
        "adetailer",
        "sd-webui-additional-networks",
        "ultimate-upscale-for-automatic1111",
        "sd-dynamic-prompts",
        "stable-diffusion-webui-images-browser",
        "sd-webui-aspect-ratio-helper",
        "openpose-editor",
        "canvas-zoom",
        "sd-webui-tunnels"
    ],
    "Quality & Enhancement": [
        "ultimate-upscale-for-automatic1111",
        "sd-webui-rembg",
        "sd-face-editor",
        "depth-lib",
        "sd-webui-segment-anything",
        "sd-webui-cutoff",
        "sd-webui-supermerger",
        "sd-webui-model-mixer"
    ],
    "Animation & Video": [
        "sd-webui-animatediff",
        "deforum-for-automatic1111-webui",
        "temporal-kit",
        "ebsynth_utility",
        "sd-webui-mov2mov"
    ],
    "Training & Fine-tuning": [
        "sd-scripts",
        "Lora-Training-in-Comfy",
        "dreambooth-training",
        "dataset-tag-editor",
        "training-picker"
    ],
    "ComfyUI Extensions": [
        "ComfyUI-Manager",
        "ComfyUI-Custom-Scripts", 
        "ComfyUI-Impact-Pack",
        "ComfyUI-Advanced-ControlNet",
        "ComfyUI-AnimateDiff-Evolved",
        "ComfyUI-VideoHelperSuite",
        "ComfyUI-WD14-Tagger",
        "ComfyUI_UltimateSDUpscale",
        "was-node-suite-comfyui",
        "efficiency-nodes-comfyui"
    ]
}

# Model URLs (Popular direct download links)
model_urls = {
    "Realistic Vision V6.0": "https://civitai.com/api/download/models/245598",
    "DreamShaper 8": "https://civitai.com/api/download/models/128713",
    "ChilloutMix": "https://civitai.com/api/download/models/11745",
    "Deliberate v2": "https://civitai.com/api/download/models/15236",
    "Anything V5": "https://civitai.com/api/download/models/90854",
    "SDXL Base 1.0": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
    "SDXL VAE": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors"
}

# VAE URLs
vae_urls = {
    "vae-ft-mse-840000": "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors",
    "blessed2.vae": "https://huggingface.co/NoCrypt/blessed_vae/resolve/main/blessed2.vae.pt",
    "ClearVAE V2.3": "https://civitai.com/api/download/models/133362",
    "orangemix.vae": "https://huggingface.co/WarriorMama777/OrangeMixs/resolve/main/VAEs/orangemix.vae.pt"
}

# Popular ControlNet URLs
controlnet_urls = {
    "Canny": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth",
    "Depth": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth.pth", 
    "OpenPose": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth",
    "Scribble": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_scribble.pth",
    "Lineart": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart.pth"
}

# Extension URLs
extension_urls = {
    "ControlNet": "https://github.com/Mikubill/sd-webui-controlnet.git",
    "ADetailer": "https://github.com/Bing-su/adetailer.git",
    "Additional Networks": "https://github.com/kohya-ss/sd-webui-additional-networks.git",
    "Ultimate Upscale": "https://github.com/Coyote-A/ultimate-upscale-for-automatic1111.git",
    "Dynamic Prompts": "https://github.com/adieyal/sd-dynamic-prompts.git",
    "Images Browser": "https://github.com/AlUlkesh/stable-diffusion-webui-images-browser.git",
    "Aspect Ratio Helper": "https://github.com/thomasasfk/sd-webui-aspect-ratio-helper.git",
    "OpenPose Editor": "https://github.com/fkunn1326/openpose-editor.git",
    "Canvas Zoom": "https://github.com/richrobber2/canvas-zoom.git",
    "Tunnels": "https://github.com/Bing-su/sd-webui-tunnels.git"
}

# Quality presets for different use cases
quality_presets = {
    "High Quality Portrait": {
        "model": "Realistic Vision V6.0",
        "vae": "vae-ft-mse-840000-ema-pruned",
        "lora": ["Detail Tweaker", "Face Enhancer"],
        "controlnet": ["OpenPose"],
        "settings": {
            "steps": 25,
            "cfg_scale": 7.5,
            "width": 512,
            "height": 768,
            "sampler": "DPM++ 2M Karras"
        }
    },
    "Anime Character": {
        "model": "Anything V5",
        "vae": "blessed2.vae",
        "lora": ["Anime Style Enhancer"],
        "controlnet": ["Canny"],
        "settings": {
            "steps": 20,
            "cfg_scale": 8.0,
            "width": 512,
            "height": 768,
            "sampler": "Euler a"
        }
    },
    "Landscape Art": {
        "model": "DreamShaper",
        "vae": "ClearVAE_V2.3",
        "lora": ["Background Enhancer", "Lighting Enhancer"],
        "controlnet": ["Depth"],
        "settings": {
            "steps": 30,
            "cfg_scale": 7.0,
            "width": 768,
            "height": 512,
            "sampler": "DPM++ SDE Karras"
        }
    },
    "SDXL High Quality": {
        "model": "SDXL Base 1.0",
        "vae": "sdxl_vae",
        "lora": ["Detail Tweaker XL"],
        "controlnet": ["SDXL Canny"],
        "settings": {
            "steps": 25,
            "cfg_scale": 7.5,
            "width": 1024,
            "height": 1024,
            "sampler": "DPM++ 2M Karras"
        }
    }
}

# Categories for organization
categories = {
    "models": {
        "Realistic": ["Realistic Vision V6.0", "Epic Realism", "AbsoluteReality"],
        "Anime": ["Anything V5", "CounterfeitXL", "MeinaMix"],
        "Artistic": ["OpenJourney", "Analog Diffusion", "Vintedois Diffusion"],
        "SDXL": ["SDXL Base 1.0", "Juggernaut XL", "RealVisXL V4.0"]
    },
    "styles": {
        "Photography": ["Photorealistic", "Portrait", "Landscape"],
        "Art": ["Oil Painting", "Watercolor", "Digital Art"],
        "Animation": ["Anime", "Cartoon", "3D Render"],
        "Vintage": ["Film Photography", "Retro", "Vintage"]
    }
}

# Helper functions
def get_models_by_category(category):
    """Get models filtered by category"""
    return categories.get("models", {}).get(category, [])

def get_popular_models(count=10):
    """Get most popular models"""
    all_models = []
    for category_models in model_list.values():
        all_models.extend(category_models)
    return all_models[:count]

def get_recommended_vae(model_name):
    """Get recommended VAE for a model"""
    anime_models = ["Anything", "Counterfeit", "Meina", "Waifu", "Animagine"]
    realistic_models = ["Realistic Vision", "Epic Realism", "Absolute", "Cyberrealistic"]
    
    if any(anime in model_name for anime in anime_models):
        return "blessed2.vae"
    elif any(realistic in model_name for realistic in realistic_models):
        return "vae-ft-mse-840000-ema-pruned"
    elif "SDXL" in model_name or "XL" in model_name:
        return "sdxl_vae"
    else:
        return "vae-ft-mse-840000-ema-pruned"

def get_preset_by_name(preset_name):
    """Get quality preset by name"""
    return quality_presets.get(preset_name, {})

def search_models(query):
    """Search for models containing the query string"""
    results = []
    query_lower = query.lower()
    
    for category, models in model_list.items():
        for model in models:
            if query_lower in model.lower():
                results.append({
                    "name": model,
                    "category": category,
                    "type": "model"
                })
    
    return results

# Export all data structures
__all__ = [
    'model_list', 'vae_list', 'lora_list', 'controlnet_list', 'extension_list',
    'model_urls', 'vae_urls', 'controlnet_urls', 'extension_urls',
    'quality_presets', 'categories',
    'get_models_by_category', 'get_popular_models', 'get_recommended_vae',
    'get_preset_by_name', 'search_models'
]
