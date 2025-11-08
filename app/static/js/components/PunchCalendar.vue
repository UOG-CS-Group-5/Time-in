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
      @click:event="onEventClick"
    ></v-calendar>

    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title>
            <span class="headline">{{ formTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-row>
              <v-col cols="6">
                <v-menu
                  v-model="showStartTimeSelect"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="290px"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="form.start_time"
                      label="Start Time"
                      prepend-icon="mdi-clock-time-four-outline"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                      format="ampm"
                    ></v-text-field>
                  </template>

                  <v-time-picker
                    v-model="form.start_time"
                    format="ampm"
                  ></v-time-picker>
                </v-menu>
              </v-col>
              <v-col cols="6">
                <v-menu
                  v-model="showEndTimeSelect"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="290px"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="form.end_time"
                      label="End Time"
                      prepend-icon="mdi-clock-time-four-outline"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                      format="ampm"
                    ></v-text-field>
                  </template>

                  <v-time-picker
                    v-model="form.end_time"
                    format="ampm"
                  ></v-time-picker>
                </v-menu>
              </v-col>
            </v-row>
            <v-text-field
                v-if="is_admin"
                v-model="form.salary_at_time"
                label="Salary"
                type="number"
                step="0.01"
                required
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              v-if="this.is_admin && this.form.origin.length > 0" color="error darken-1" text
              @click="deletePunches"
            >Delete</v-btn>
            <!-- <v-btn 
              v-if="this.is_admin && this.form.origin.length > 0" color="blue darken-1" text 
              @click="savePunch"
            >Save</v-btn> -->
            <v-btn 
              v-if="this.is_admin && (this.form.origin.length == 0 || this.form.origin.length == 1 && this.form.end_time)" color="blue darken-1" text 
              @click="addPunches"
            >Create</v-btn>
            <v-btn color="blue darken-1" text @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbars (drop down popup) -->
    <v-snackbar v-model="errorSnackbar" color="red" top>
      {{ errorMessage }}
      <v-btn color="white" text @click="errorSnackbar = false">Close</v-btn>
    </v-snackbar>

    <v-snackbar v-model="successSnackbar" color="green" top>
      {{ successMessage }}
      <v-btn color="white" text @click="successSnackbar = false">Close</v-btn>
    </v-snackbar>
  </v-container>
</template>

<script>
const EMPTY_FORM = {
  start_date: null,
  start_time: null,
  end_date: null,
  end_time: null,
  salary_at_time: null,
  origin: []
}

module.exports = {
  name: "PunchCalendar",
  props: {
    user_id: { type: Number, required: false, default: null },
    is_admin: { type: Boolean, required: false, default: false },
    salary: { type: Number, required: true }
  },
  data() {
    return {
      start_time: "12:30",
      punches: [],
      currentDate: new Date(),
      timeSelect: [],
      form: {...EMPTY_FORM},
      prev_form_start_time: null,
      dialog: false,
      showStartTimeSelect: false,
      showEndTimeSelect: false,
      punch_map: [],
      errorSnackbar: false,
      errorMessage: "",
      successSnackbar: false,
      successMessage: "",
    };
  },
  computed: {
    formTitle() {
      let title = "Time Range"
      if (this.form.origin.length > 0) {
        title = "Time Punch"
        // no editing allowed
        // must delete and make a new one
        // if (is_admin) {
        //   title = "Edit " + title
        // }
      }
      return title
    },
    events() {
      const ret = []
      let punch = {origin: []}
      this.punches.forEach((p) => {
        const {id, type, salary_at_time, dt} = p
        // format date so calendar can use it
        let d = this.formatDate(dt)
        if (type == "IN") {
          punch.start = d
          punch.salary = parseFloat(salary_at_time)
          punch.origin.push(id)
        } else {
          punch.end = d
          punch.origin.push(id)
          ret.push(punch)
          punch = {origin: []}
        }
        this.punch_map[id] = p
      });
      // in punch without an out
      if (punch.start) {
        ret.push(punch)
      }
      if (this.timeSelect.length > 0) {
        punch = {origin: []}
        punch.start = this.formatDate(this.timeSelect[0])
        if (this.timeSelect.length == 2) {
          punch.end = this.formatDate(this.timeSelect[1])
        }
        punch.color = "primary lighten-3"
        ret.push(punch)
      }
      return ret
    }
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
    closeDialog() {
      this.dialog = false
    },
    onTimeClick({ date, time }) {
      const dt = new Date(date)
      const [hour, min] = time.split(':').map(v => parseInt(v))
      dt.setHours(hour, min, 0, 0)
      if (this.timeSelect.length == 2) {
        this.timeSelect = []
      } else if (this.timeSelect.length == 1) {
        if (dt < this.timeSelect[0]) {
          this.timeSelect.unshift(dt)
        } else {
          this.timeSelect.push(dt)
        }
      } else {
        this.timeSelect.push(dt)
      }
    },
    onEventClick({ event }, nativeEvent) {
      const nf = {...EMPTY_FORM, origin: []}
      nf.start_date = event.start.slice(0,10)
      nf.start_time = event.start.slice(11)
      nf.salary_at_time = event.salary || this.salary
      if (event.origin.length > 0) nf.origin.push(event.origin[0])
      if (event.end) {
        nf.end_date = event.end.slice(0,10)
        nf.end_time = event.end.slice(11)
        if (event.origin.length > 1) nf.origin.push(event.origin[1])
      }
      this.form = nf
      this.dialog = true
      nativeEvent.stopPropagation()
    },
    // savePunch() {

    // },
    async addPunches() {
      let ds = new Date(`${this.form.start_date} ${this.form.start_time}`).toISOString()
      let de = this.form.end_date ? new Date(`${this.form.end_date} ${this.form.end_time}`).toISOString() : null
      if (this.form.origin.length == 1 && this.form.end_time) {
        // date from start, time from end
        ds = new Date(`${this.form.start_date} ${this.form.end_time}`).toISOString()
        de = null
      }
      await this.punchClockFetch(this.user_id || null, ds, de, this.form.salary_at_time)
      this.dialog = false
      this.timeSelect = []
    },
    async punchClockFetch(userId = null, datetime = null, datetimeEnd = null, salary = null) {
      try {
        const params = new URLSearchParams();

        if (userId !== null) params.append('user_id', userId);
        if (datetime) params.append('datetime', datetime);
        if (datetimeEnd) params.append('datetime_end', datetimeEnd);
        if (salary !== null) params.append('salary', salary);

        const url = `/punch?${params.toString()}`;

        const response = await fetch(url, { method: 'POST' });

        if (!response.ok) {
          const errorText = await response.text(); // backend returns string on error
          this.errorMessage = errorText;
          this.errorSnackbar = true;
          return;
        }

        const data = await response.json();

        await this.fetchPunches();

        this.successMessage = `Punch${datetimeEnd ? 'es' : ''} added successfully`;
        this.successSnackbar = true;

        return data.new_punches;

      } catch (err) {
        this.errorMessage = 'Failed to punch. Please try again.';
        this.errorSnackbar = true;
        console.error(err);
      }
    },
    async deletePunches() {
      if (this.form.origin.length == 0) {
        console.error('No punch to delete')
        return
      }
      peid = null
      if (this.form.origin.length > 1) {
        peid = this.form.origin[1]
      }

      await this.deletePunchesFetch(this.form.origin[0], peid)
      this.dialog = false
    },
    async deletePunchesFetch(punchId, punchEndId = null) {
      try {
        let url = `/punch?punch_id=${punchId}`;
        if (punchEndId) url += `&punch_end_id=${punchEndId}`;

        const response = await fetch(url, { method: 'DELETE' });

        if (!response.ok) {
          const errorText = await response.text(); // backend returns string error
          this.errorMessage = errorText;
          this.errorSnackbar = true;
          return;
        }

        await this.fetchPunches();

        // Feedback to user
        this.successMessage = 'Punch deleted successfully';
        this.successSnackbar = true;

      } catch (err) {
        this.errorMessage = 'Failed to delete punch. Please try again.';
        this.errorSnackbar = true;
        console.error(err);
      }
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
        o.dt = new Date(o.timestamp.slice(0, 19) + 'Z')
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
    },
    async getClosestSalary(datetime) {
      try {
        // Ensure the date is ISO formatted for the Flask endpoint
        const isoDate = new Date(datetime).toISOString();

        const url = `/punch/closest_salary?user_id=${this.user_id}&datetime=${isoDate}`;

        const response = await fetch(url, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          const errMsg = await response.text();
          throw new Error(errMsg || "Error fetching salary");
        }

        const data = await response.json();
        return data.salary;
      } catch (error) {
        console.log("Failed to get closest salary:", error);
        return null;
      }
    }
  },
  async mounted() {
    await this.fetchPunches();
  },
  watch: {
    user_id() {
      this.timeSelect = []
      this.fetchPunches()
    },
    form: {
      async handler(newValue, oldVaue) {
        if (`${newValue.start_time}` != `${oldVaue.start_time}`) {
          let salary = await this.getClosestSalary(`${newValue.start_date} ${newValue.start_time}`)
          if (salary !== null) {
            this.form.salary_at_time = salary
          } else {
            this.form.salary_at_time = this.salary
          }
        }
      },
      deep: true
    }
  }
};
</script>

<style>
.v-calendar-daily__body {
  max-height: 600px;
  overflow: scroll;
}
</style>
