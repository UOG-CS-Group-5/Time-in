<template>
    <v-container>
        <v-text-field 
            v-model="example"
            label="Example"
        ></v-text-field>
        <p>The text: {{ example }}</p>

        <punch-calendar
            :salary="salary"
            :user_id="user_id"
        />
    </v-container>
</template>

<script>
const PunchCalendar = httpVueLoader("/static/js/components/PunchCalendar.vue")

module.exports = {
    props: {
        salary: { type: Number, required: true },
        user_id: { type: Number, required: true }
    },
    components: {
        PunchCalendar
    },
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