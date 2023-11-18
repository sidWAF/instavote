FROM schoolofdevops/vote-result:latest


RUN mkdir -p /app
WORKDIR /app
# build in jenkins
RUN npm config set unsafe-perm true
RUN npm install -g nodemon
RUN npm config set registry https://registry.npmjs.org
COPY /result/package.json /app/package.json
COPY /result/server.js /app/server.js
COPY /result/views/* /app/views/*
RUN npm install \
 && npm ls \
 && npm cache clean --force \
 && mv /app/node_modules /node_modules
COPY . /app

ENV PORT 80
EXPOSE 80

CMD ["node", "server.js"]
