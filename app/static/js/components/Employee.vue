<template>
    <v-container>
        <v-text-field 
            v-model="example"
            label="Example"
        ></v-text-field>
        <p>The text: {{ example }}</p>
    </v-container>
</template>

<script>
module.exports = {
    data() {
        return {
            // define reactive variables 
            // to be used within component
            example: "field"
        }
    },
    methods: {
        // define methods to be used within component
    },
    async mounted() {
        // do something once component is mounted
    }
}
</script>

<style>
    /* optional styles scoped specifically 
       to this component */
</style>