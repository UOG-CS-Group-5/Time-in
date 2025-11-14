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
}
</script>