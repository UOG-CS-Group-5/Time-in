<template>
  <v-container>

    <v-row class="my-2" justify="space-between">
      <v-btn color="primary" @click="prevWeek">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <div>
        <v-btn color="primary" @click="() => punchClockFetch(user_id)">
          <v-icon>mdi-clock</v-icon>
        </v-btn>
        <v-btn color="primary" @click="nextWeek">
          <v-icon>mdi-arrow-right</v-icon>
        </v-btn>
      </div>
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
              <!-- start time -->
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
                      :disabled="form.origin.length > 0"
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
              <!-- end time -->
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
                      :disabled="form.origin.length == 2"
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
              <v-row>
                <v-col cols="6">
                  <v-text-field
                      v-model="form.salary_at_time"
                      label="Salary"
                      type="number"
                      step="0.01"
                      :required="is_admin"
                      :disabled="!is_admin"
                  ></v-text-field>
                </v-col>
                <v-col cols="6"
                  class="d-flex align-center justify-center"
                >
                  <p class="ma-0"
                    v-if="payForSelectedTime !== null"
                  >
                    Total Pay <b>${{ payForSelectedTime?.toFixed(2) }}</b>
                  </p>
                </v-col>
              </v-row>
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
      // list of punches
      punches: [],
      // current day/week looking at
      currentDate: new Date(),
      // selected times
      timeSelect: [],
      // form fields
      form: {...EMPTY_FORM},
      prev_dialog: false,
      dialog: false,
      showStartTimeSelect: false,
      showEndTimeSelect: false,
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
      // convert from punch entries
      // into events with start/end times
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
      });
      // in punch without an out
      if (punch.start) {
        ret.push(punch)
      }
      // add selected datetimes with lighter color
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
    },
    payForSelectedTime() {
      // only calculate pay if punch dialog is open
      if (!this.dialog) {
        return null;
      }

      // if both time fields have data, calculate pay
      if (this.form.start_time && this.form.end_time) {
        return this.calculatePay(
          new Date(`${this.form.start_date} ${this.form.start_time}`), 
          new Date(`${
              this.form.end_date ? this.form.end_date : this.form.start_date
            } ${this.form.end_time}`))
      } else {
        return null
      }
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
      // convert time clicked into a datetime
      const dt = new Date(date)
      const [hour, min] = time.split(':').map(v => parseInt(v))
      dt.setHours(hour, min, 0, 0)
      // if clicked third time, deselect everything
      if (this.timeSelect.length == 2) {
        this.timeSelect = []
      } else if (this.timeSelect.length == 1) {
        // put 2nd datetime selected in in order
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
      // prep form
      const nf = {...EMPTY_FORM, origin: []}
      nf.start_date = event.start.slice(0,10)
      nf.start_time = event.start.slice(11)
      nf.salary_at_time = event.salary !== null && event.salary || this.salary
      if (event.origin.length > 0) nf.origin.push(event.origin[0])
      if (event.end) {
        nf.end_date = event.end.slice(0,10)
        nf.end_time = event.end.slice(11)
        if (event.origin.length > 1) nf.origin.push(event.origin[1])
      }
      // open form
      this.form = nf
      this.dialog = true
      // stop from selecting time
      nativeEvent.stopPropagation()
    },
    // savePunch() {

    // },
    async addPunches() {
      // convert datetime field strings into datetimes
      let ds = new Date(`${this.form.start_date} ${this.form.start_time}`).toISOString()
      let de = this.form.end_date ? new Date(`${this.form.end_date} ${this.form.end_time}`).toISOString() : null
      // if this is a punch without an OUT time, set it up to submit a new single punch
      if (this.form.origin.length == 1 && this.form.end_time) {
        // date from start, time from end
        ds = new Date(`${this.form.start_date} ${this.form.end_time}`).toISOString()
        de = null
      }
      // add punch(es)
      await this.punchClockFetch(this.user_id || null, ds, de, this.form.salary_at_time)
      // close dialog and deselect times
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
      // track punch order for pay calculation later
      let i = 0
      this.punches = data.punches.map(o => {
        // remove time smaller than seconds (after decimal)
        o.dt = new Date(o.timestamp.slice(0, 19) + 'Z')
        o.i = i;
        i += 1
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
    },
    calculatePay(start_date, end_date) {
      let sum = 0
      // start out with in date values 
      // in case we start with an OUT punch
      let in_date = start_date
      // since we calculate it on form open
      let salary = this.form.salary_at_time
      let accounted_for = false
      let ith = 0
      this.punches
        // filter punches within time range
        .filter(({dt}) => start_date <= dt && dt <= end_date)
        .forEach(({type, salary_at_time, dt, i}) => {
          if (type == "IN") {
            in_date = dt
            salary = salary_at_time
            accounted_for = false
          } else {
            hours_elapsed = (dt - in_date)/1000/60/60
            sum += hours_elapsed * salary
            accounted_for = true
          }
          ith = i
        })
      // clocked in time that wasn't accounted for
      // if unaccounted for punch was last punch
      // it's missing an end punch and we can ignore it
      if (!accounted_for && ith !== this.punches.length - 1) {
        hours_elapsed = (end_date - in_date)/1000/60/60
        sum += hours_elapsed * salary
      }
      return sum
    },
    async adjustSalary(date) {
      let salary = await this.getClosestSalary(date)
      if (salary !== null) {
        this.form.salary_at_time = salary
      } else {
        this.form.salary_at_time = this.salary
      }
    }
  },
  async mounted() {
    await this.fetchPunches();
  },
  watch: {
    // if user_id changes, deselect datetimes and grab that user's punches
    user_id() {
      this.timeSelect = []
      this.fetchPunches()
    },
    dialog(newValue, oldVaue) {
      this.prev_dialog = oldVaue
      // only adjust salary if the punch doesn't exist
      if (this.form.origin.length !== 0) {
        return
      }
      if (newValue) {
        this.adjustSalary(`${this.form.start_date} ${this.form.start_time}`)
      }
    },
    form: {
      async handler(newValue, oldVaue) {
        // only adjust salary if the punch doesn't exist
        if (this.form.origin.length !== 0) {
          return
        }
        // if form form.start_time changes, 
        // change salary to the closest salary
        if (`${newValue.start_time}` != `${oldVaue.start_time}`) {
          await this.adjustSalary(`${newValue.start_date} ${newValue.start_time}`)
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
