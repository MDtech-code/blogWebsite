from decouple import config 
FRONTEND_URL=config('FRONTEND_URL')
def generate_share_url(platform, post):
    base_url = f'{FRONTEND_URL}/blog/post/{post.id}/'
    if platform == 'Facebook':
        return f'https://www.facebook.com/sharer/sharer.php?u={base_url}'
    elif platform == 'Twitter':
        return f'https://twitter.com/intent/tweet?url={base_url}&text={post.title}'
    elif platform == 'Instagram':
        return f'https://www.instagram.com/?url={base_url}'
    elif platform == 'WhatsApp':
        return f'https://api.whatsapp.com/send?text={base_url}'
    else:
        return base_url
