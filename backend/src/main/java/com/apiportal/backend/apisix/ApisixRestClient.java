package com.apiportal.backend.apisix;


import com.apiportal.backend.apisix.models.Consumer;
import com.apiportal.backend.apisix.models.KeyAuth;
import com.apiportal.backend.apisix.models.Plugins;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.json.JSONException;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
@Service
public class ApisixRestClient {

    @Value("${apisix.consumersUrl}")
    private String consumersUrl;

    @Value("${apisix.adminApiKey}")
    private String adminApiKey;

    @Value("${apisix.keyPath}")
    private String keyPath;

    @Value("${apisix.keyName}")
    private String keyName;


    public void createConsumer(String username) throws JSONException, JsonProcessingException {

        RestTemplate restTemplate = new RestTemplate();

        ObjectMapper mapper = new ObjectMapper();
        String str = mapper.writeValueAsString(createConsumerObject(username));
        JSONObject jsonObject = new JSONObject(str);


        HttpEntity<String> request = new HttpEntity<String>(jsonObject.toString(), generateHeaders());

        try {
            HttpEntity<String> response = restTemplate.exchange(consumersUrl, HttpMethod.PUT, request, String.class);
        } catch (RestClientException e) {
            throw e;
        }
    }

    private HttpHeaders generateHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-API-KEY",adminApiKey);
        return headers;
    }

    private Consumer createConsumerObject(String username) {
        Consumer consumer = new Consumer();
        consumer.setUsername(username);

        KeyAuth keyAuth = new KeyAuth();
        keyAuth.setKey(keyPath+username+"/"+keyName);
        Plugins plugins = new Plugins();
        plugins.setKeyAuth(keyAuth);
        consumer.setPlugins(plugins);
        return consumer;
    }
}
