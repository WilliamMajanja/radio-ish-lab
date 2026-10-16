# Radio-ish Lab — Season One EPK microsite image.
#
# Multi-stage: build the static site from the tracked source (tools/build_site.py),
# then serve it with nginx. Build from the repo root:
#
#     docker build -f deploy/Dockerfile -t radio-ish-lab:season-one .
#
# The build context carries only metadata/press copy (see ../../.dockerignore);
# the ~160 GiB of masters are never part of the image.

FROM python:3.12-alpine AS build
WORKDIR /src
COPY tools/requirements.txt tools/requirements.txt
RUN pip install --no-cache-dir -r tools/requirements.txt
COPY . .
RUN python tools/build_site.py --out /site

FROM nginx:1.27-alpine
LABEL org.opencontainers.image.title="Radio-ish Lab — Season One" \
      org.opencontainers.image.description="Static EPK microsite for Radio-ish Lab, Season One." \
      org.opencontainers.image.licenses="See LICENSE" \
      org.opencontainers.image.source="https://github.com/djbernie-cyber/radio-ish-lab"
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /site /usr/share/nginx/html
EXPOSE 80
