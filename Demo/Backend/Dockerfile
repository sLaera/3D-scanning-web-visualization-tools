#This Dockerfile utilizes stesp defined in externals/Dockerfile as a base to than start server

#------ Install and start Nest--------
FROM build-externals AS final
WORKDIR /app
#Externals are managed in previous steps
COPY . .
RUN npm install
EXPOSE 3000