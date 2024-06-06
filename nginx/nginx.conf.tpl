client_max_body_size 8M;

upstream django_app {
    server tavarat-kiertoon:8989;
}

server {

    listen 8000 ssl default;
    server_name ${DOMAIN};

    ssl_certificate ${SSL_CERT};
    ssl_certificate_key ${SSL_KEY};
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    client_max_body_size 50M;

    error_page 497 301 =301 https://$host:$server_port$request_uri;

    location / {
        proxy_pass https://django_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Ssl on;
        proxy_set_header Host $host:$server_port;
        proxy_redirect off;
    }

    location /media {
        alias /medias/;
    }

    location /pictures {
        alias /medias/pictures/;
    }

    location /static {
        alias /static/;
        autoindex off;
    }

}