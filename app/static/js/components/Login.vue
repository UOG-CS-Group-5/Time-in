<template>
    <v-container>
        <h1>Login</h1>
        <v-form method="POST" action="/login">
            <v-text-field
                label="Username"
                name="username"
                required
            ></v-text-field>
            <v-text-field
                label="Password"
                name="password"
                type="password"
                required
            ></v-text-field>
            <v-btn type="submit" color="primary">Login</v-btn>
        </v-form>
    </v-container>
</template>
