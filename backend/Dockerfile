FROM maven:3.8.4-openjdk-17 AS build
RUN mkdir -p /workspace
WORKDIR /workspace
COPY pom.xml /workspace
COPY src /workspace/src
ENV JAVA_TOOL_OPTIONS -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
ENV JAVA_DEBUG_PORT 5005
RUN mvn -f pom.xml clean package -DskipTests

FROM openjdk:17-alpine
COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8082 5005
ENTRYPOINT ["java","-jar","-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005","app.jar"]