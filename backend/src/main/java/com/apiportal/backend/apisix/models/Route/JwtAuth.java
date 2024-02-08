
package com.apiportal.backend.apisix;

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
    "header",
    "query",
    "hide_credentials",
    "cookie"
})
@Generated("jsonschema2pojo")
public class JwtAuth {

    @JsonProperty("header")
    private String header;
    @JsonProperty("query")
    private String query;
    @JsonProperty("hide_credentials")
    private Boolean hideCredentials;
    @JsonProperty("cookie")
    private String cookie;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("header")
    public String getHeader() {
        return header;
    }

    @JsonProperty("header")
    public void setHeader(String header) {
        this.header = header;
    }

    @JsonProperty("query")
    public String getQuery() {
        return query;
    }

    @JsonProperty("query")
    public void setQuery(String query) {
        this.query = query;
    }

    @JsonProperty("hide_credentials")
    public Boolean getHideCredentials() {
        return hideCredentials;
    }

    @JsonProperty("hide_credentials")
    public void setHideCredentials(Boolean hideCredentials) {
        this.hideCredentials = hideCredentials;
    }

    @JsonProperty("cookie")
    public String getCookie() {
        return cookie;
    }

    @JsonProperty("cookie")
    public void setCookie(String cookie) {
        this.cookie = cookie;
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
