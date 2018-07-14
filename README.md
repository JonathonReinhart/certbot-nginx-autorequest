certbot-nginx-autorequest
=========================
This is a simple-ish tool that will simplify requesting a LetsEncrypt
certificate using certbot, when running lots of domains on NGINX.

It will automatically detect all `ssl` sites configured in
`/etc/nginx/sites-enabled`, and request a certificate that covers all of their
server names. It also handles the webroot option for each site, to
[avoid having to enter them manually every time](https://community.letsencrypt.org/t/avoid-re-entering-webroot-when-requesting-new-certificate/66709).
