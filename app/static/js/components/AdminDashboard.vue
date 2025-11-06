<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Admin Dashboard</h1>
                <v-btn color="primary" @click="openAddUserDialog">Add User</v-btn>
            </v-col>
        </v-row>

        <v-row>
            <v-col>
                <!-- data table using the defined headers and items -->
                <v-data-table
                    :headers="headers"
                    :items="users"
                    item-value="id"
                    class="elevation-1"
                >
                    <template v-slot:top>
                        <v-toolbar flat>
                            <v-toolbar-title>Users</v-toolbar-title>
                            <v-spacer></v-spacer>
                        </v-toolbar>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <!-- pencil to edit user -->
                        <v-btn icon @click="openEditUserDialog(item)">
                            <v-icon>mdi-pencil</v-icon>
                        </v-btn>
                        <!-- trash can to delete -->
                        <v-btn icon @click="deleteUser(item.id)">
                            <v-icon>mdi-delete</v-icon>
                        </v-btn>
                    </template>
                    <template v-slot:item.salary="{ item }">
                        <!-- display with 2 decimals -->
                        {{ item.salary.toFixed(2) }}
                    </template>
                </v-data-table>
            </v-col>
        </v-row>

        <!-- Add/Edit User Dialog -->
        <v-dialog v-model="dialog" max-width="500px">
            <v-card>
                <v-card-title>
                    <span class="headline">{{ dialogTitle }}</span>
                </v-card-title>
                <v-card-text>
                    <v-form ref="form">
                        <v-text-field
                            v-model="form.username"
                            label="Username"
                            required
                        ></v-text-field>
                        <v-text-field
                            v-model="form.password"
                            label="Password"
                            type="password"
                            :rules="[isEdit ? () => true : passwordRequired]"
                        ></v-text-field>
                        <v-checkbox v-model="form.is_admin" label="Admin"></v-checkbox>
                        <v-text-field
                            v-model="form.salary"
                            label="Salary"
                            type="number"
                            step="0.01"
                            required
                        ></v-text-field>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" text @click="closeDialog">Cancel</v-btn>
                    <v-btn color="blue darken-1" text @click="saveUser">Save</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Error Snackbar (drop down popup) -->
        <v-snackbar v-model="errorSnackbar" color="red" top>
            {{ errorMessage }}
            <v-btn color="white" text @click="errorSnackbar = false">Close</v-btn>
        </v-snackbar>
    </v-container>
</template>

<script>
module.exports = {
    data() {
        return {
            users: [],
            headers: [
                { text: "ID", value: "id" },
                { text: "Username", value: "username" },
                { text: "Admin", value: "is_admin" },
                { text: "Salary", value: "salary" },
                { text: "Actions", value: "actions", sortable: false },
            ],
            dialog: false,
            dialogTitle: "",
            form: {
                id: null,
                username: "",
                password: "",
                is_admin: false,
                salary: 0.0,
            },
            // variable to tell us what action to take
            // when adding or editing users
            isEdit: false,
            passwordRequired: value => !!value || 'Password is required',
            errorSnackbar: false,
            errorMessage: "",
        };
    },
    methods: {
        async fetchUsers() {
            try {
                const response = await fetch("/admin/users");
                if (!response.ok) {
                    throw new Error("Failed to fetch users");
                }
                this.users = await response.json();
            } catch (error) {
                this.errorMessage = "Failed to fetch users. Please try again.";
                this.errorSnackbar = true;
            }
        },
        openAddUserDialog() {
            this.dialogTitle = "Add User";
            this.isEdit = false;
            this.form = { id: null, username: "", password: "", is_admin: false, salary: 0.0 };
            this.dialog = true;
        },
        openEditUserDialog(user) {
            this.dialogTitle = "Edit User";
            this.isEdit = true;
            this.form = { ...user, password: "" }; // Don't prefill the password
            this.dialog = true;
        },
        async saveUser() {
            try {
                const url = this.isEdit ? `/admin/users/${this.form.id}` : "/admin/users";
                const method = this.isEdit ? "PUT" : "POST";
                const response = await fetch(url, {
                    method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(this.form),
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    this.errorMessage = errorData.error || "An error occurred.";
                    this.errorSnackbar = true;
                    return;
                }
                this.fetchUsers();
                this.closeDialog();
            } catch (error) {
                this.errorMessage = "Failed to save user. Please try again.";
                this.errorSnackbar = true;
            }
        },
        async deleteUser(userId) {
            let response;
            try {
                response = await fetch(`/admin/users/${userId}`, { method: "DELETE" });
                if (!response.ok) {
                    const errorData = await response.json()
                    this.errorMessage = errorData.error || "Failed to delete user. Please try again.";
                    this.errorSnackbar = true;
                    return;
                }
                this.fetchUsers();
            } catch (error) {
                this.errorMessage = "Failed to delete user. Please try again.";
                this.errorSnackbar = true;
            }
        },
        closeDialog() {
            this.dialog = false;
        },
    },
    async mounted() {
        await this.fetchUsers();
    },
};
</script>