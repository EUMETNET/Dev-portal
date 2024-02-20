
package com.apiportal.backend.apisix.models.Route;

import java.util.LinkedHashMap;
import java.util.Map;
import javax.annotation.Generated;


import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "jwt-auth",
    "key-auth"
})
@Generated("jsonschema2pojo")
public class Plugins {

    @JsonProperty("jwt-auth")
    private JwtAuth jwtAuth;
    @JsonProperty("key-auth")
    private KeyAuth keyAuth;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("jwt-auth")
    public JwtAuth getJwtAuth() {
        return jwtAuth;
    }

    @JsonProperty("jwt-auth")
    public void setJwtAuth(JwtAuth jwtAuth) {
        this.jwtAuth = jwtAuth;
    }

    @JsonProperty("key-auth")
    public KeyAuth getKeyAuth() {
        return keyAuth;
    }

    @JsonProperty("key-auth")
    public void setKeyAuth(KeyAuth keyAuth) {
        this.keyAuth = keyAuth;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

}
