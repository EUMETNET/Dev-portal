
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
    "value",
    "key",
    "createdIndex",
    "modifiedIndex"
})
@Generated("jsonschema2pojo")
public class List {

    @JsonProperty("value")
    private Value value;
    @JsonProperty("key")
    private String key;
    @JsonProperty("createdIndex")
    private Integer createdIndex;
    @JsonProperty("modifiedIndex")
    private Integer modifiedIndex;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("value")
    public Value getValue() {
        return value;
    }

    @JsonProperty("value")
    public void setValue(Value value) {
        this.value = value;
    }

    @JsonProperty("key")
    public String getKey() {
        return key;
    }

    @JsonProperty("key")
    public void setKey(String key) {
        this.key = key;
    }

    @JsonProperty("createdIndex")
    public Integer getCreatedIndex() {
        return createdIndex;
    }

    @JsonProperty("createdIndex")
    public void setCreatedIndex(Integer createdIndex) {
        this.createdIndex = createdIndex;
    }

    @JsonProperty("modifiedIndex")
    public Integer getModifiedIndex() {
        return modifiedIndex;
    }

    @JsonProperty("modifiedIndex")
    public void setModifiedIndex(Integer modifiedIndex) {
        this.modifiedIndex = modifiedIndex;
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
