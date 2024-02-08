
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
    "nodes",
    "hash_on",
    "pass_host",
    "type",
    "scheme"
})
@Generated("jsonschema2pojo")
public class Upstream {

    @JsonProperty("nodes")
    private Nodes nodes;
    @JsonProperty("hash_on")
    private String hashOn;
    @JsonProperty("pass_host")
    private String passHost;
    @JsonProperty("type")
    private String type;
    @JsonProperty("scheme")
    private String scheme;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("nodes")
    public Nodes getNodes() {
        return nodes;
    }

    @JsonProperty("nodes")
    public void setNodes(Nodes nodes) {
        this.nodes = nodes;
    }

    @JsonProperty("hash_on")
    public String getHashOn() {
        return hashOn;
    }

    @JsonProperty("hash_on")
    public void setHashOn(String hashOn) {
        this.hashOn = hashOn;
    }

    @JsonProperty("pass_host")
    public String getPassHost() {
        return passHost;
    }

    @JsonProperty("pass_host")
    public void setPassHost(String passHost) {
        this.passHost = passHost;
    }

    @JsonProperty("type")
    public String getType() {
        return type;
    }

    @JsonProperty("type")
    public void setType(String type) {
        this.type = type;
    }

    @JsonProperty("scheme")
    public String getScheme() {
        return scheme;
    }

    @JsonProperty("scheme")
    public void setScheme(String scheme) {
        this.scheme = scheme;
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
