<template>
  <v-container>

    <v-row class="my-2" justify="space-between">
      <v-btn color="primary" @click="prevWeek">prev week</v-btn>
      <v-btn color="primary" @click="nextWeek">next week</v-btn>
    </v-row>

    <v-calendar
      ref="calendar"
      v-model="currentDate"
      :events="events"
      type="week"
      @click:time="onTimeClick"
    ></v-calendar>

    <v-dialog>

    </v-dialog>
    
  </v-container>
</template>

<script>
module.exports = {
  name: "PunchCalendar",
  props: {
    user_id: { type: Number, required: false, default: null }
  },
  data() {
    return {
      value: '', // Current month/week/day displayed
      punches: [],
      currentDate: new Date()
    };
  },
  computed: {
    events() {
      const ret = []
      let punch = {}
      this.punches.forEach(({type, salary_at_time, dt}) => {
        // format date so calendar can use it
        let d = this.formatDate(dt)
        if (type == "IN") {
          punch.start = d
          punch.salary = parseFloat(salary_at_time)
        } else {
          punch.end = d
          ret.push(punch)
          punch = {}
        }
      });
      // in punch without an out
      if (punch.start) {
        ret.push({...punch, end: punch.start})
      }
      return ret
    },
    // minTime() {
    //   if (!this.events.length) return "08:00"; // fallback
    //   const times = this.events.map(e => new Date(e.start));
    //   const earliest = new Date(Math.min(...times));
    //   return earliest.toTimeString().slice(0, 5);
    // },
    // maxTime() {
    //   if (!this.events.length) return "17:00"; // fallback
    //   const times = this.events.map(e => new Date(e.end));
    //   const latest = new Date(Math.max(...times));
    //   return latest.toTimeString().slice(0, 5);
    // }
  },
  methods: {
    prevWeek() {
      const d = new Date(this.currentDate);
      d.setDate(d.getDate() - 7);  // go back 7 days
      this.currentDate = d.toISOString().substr(0, 10);
    },
    nextWeek() {
      const d = new Date(this.currentDate);
      d.setDate(d.getDate() + 7);  // go forward 7 days
      this.currentDate = d.toISOString().substr(0, 10);
    },
    onTimeClick({ date, time }) {
      const dt = new Date(date)
      const [hour, min] = time.split(':').map(v => parseInt(v))
      dt.setHours(hour, min, 0, 0)
      window.alert(dt)
    },
    async fetchPunches() {
      let query = ''
      if (this.user_id) {
        query = `?user_id=${this.user_id}`
      }
      const resp = await fetch(`/punch${query}`);
      const data = await resp.json();
      this.punches = data.punches.map(o => {
        // js date obj is up to milliseconds
        o.dt = new Date(o.timestamp.slice(0, 23) + 'Z')
        return o
      });
    },
    formatDate(date) {
      const pad = n => String(n).padStart(2, '0');
      
      const year = date.getFullYear();
      const month = pad(date.getMonth() + 1);
      const day = pad(date.getDate());
      const hour = pad(date.getHours());
      const minute = pad(date.getMinutes());
      const second = pad(date.getSeconds());

      return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
    }
  },
  async mounted() {
    await this.fetchPunches();
  },
  watch: {
    user_id: "fetchPunches"
  }
};
</script>

<style>
.v-calendar-daily__body {
  max-height: 600px;
  overflow: scroll;
}
</style>
