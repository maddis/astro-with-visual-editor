#!/bin/bash

# Create necessary directories
mkdir -p public/wp-content/uploads/2021/09
mkdir -p public/wp-content/uploads/2024/04
mkdir -p public/wp-content/uploads/elementor/thumbs
mkdir -p public/wp-content/plugins/elementor-pro/assets/css/modules
mkdir -p public/wp-includes/js/jquery/ui
mkdir -p public/wp-content/themes/buddyboss-theme/assets/images
mkdir -p public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts

# Copy image files
cp tmp/wp-content/uploads/2021/09/We-Love-Pets-Logo-red.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/BBC-Studio-Dog-Leads.jpeg public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/We-Love-Pets-White-House.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/We-Love-Pets-White-House-744x1024.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/BBC.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/Channel-4.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/Telegraph-1.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/INews.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2021/09/Daily-Mail.png public/wp-content/uploads/2021/09/
cp tmp/wp-content/uploads/2024/04/sky7818.jpeg public/wp-content/uploads/2024/04/

# Copy Elementor thumbs
cp tmp/wp-content/uploads/elementor/thumbs/Jason-and-Mandy-scaled-qwo0rcujkyu4mmu1cj63xyw65tsz3kq9qrg93igiig.jpg public/wp-content/uploads/elementor/thumbs/
cp tmp/wp-content/uploads/elementor/thumbs/Nadine-11-min-scaled-qwo0rkd93n4f7ij44mf4hwzuwwrwt5k4fso4xq5d4o.jpg public/wp-content/uploads/elementor/thumbs/
cp tmp/wp-content/uploads/elementor/thumbs/bunny-in-arms-qwo0s5zjgty0mjnpmdrjl9jgkrtcq6xy6roaz39b5k.jpg public/wp-content/uploads/elementor/thumbs/
cp tmp/wp-content/uploads/elementor/thumbs/south-cambs-14-scaled-qwo0rglwcaz9x2okqksm7xy0jdafyd573a270maxtk.jpeg public/wp-content/uploads/elementor/thumbs/
cp tmp/wp-content/uploads/elementor/thumbs/1-min-scaled-qwo0rdsdrsvey8so71kqignmr7ocb9u02w3qksf4c8.jpg public/wp-content/uploads/elementor/thumbs/
cp tmp/wp-content/uploads/elementor/thumbs/Lisa-min-scaled-qwo0rhjqj50k8on7l378sfph4r5t628xfepohw9jnc.jpg public/wp-content/uploads/elementor/thumbs/

# Copy Font Awesome webfonts
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-regular-400.woff2 public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-solid-900.woff2 public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-brands-400.woff2 public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-regular-400.woff public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-solid-900.woff public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-brands-400.woff public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-regular-400.ttf public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-solid-900.ttf public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/
cp tmp/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/fa-brands-400.ttf public/wp-content/plugins/elementor/assets/lib/font-awesome/webfonts/

# Copy other assets
cp tmp/wp-content/plugins/elementor-pro/assets/css/modules/sticky.min.css public/wp-content/plugins/elementor-pro/assets/css/modules/
cp tmp/wp-includes/js/jquery/ui/core.min.js public/wp-includes/js/jquery/ui/
cp tmp/wp-content/themes/buddyboss-theme/assets/images/adminbar-background.png public/wp-content/themes/buddyboss-theme/assets/images/
