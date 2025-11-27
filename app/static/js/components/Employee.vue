<template>
    <v-container>
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
    // reactive data goes here
    data: {

    },
    // computed variables
    // get recomputed when their dependencies change
    computed: {

    },
    // methods accessible to template go here
    methods: {
        
    },
    // do code once mounted onto DOM
    mounted() {
        
    }
}
</script>

<style>
    /* custom styles for this component */
</style>