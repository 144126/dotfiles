// full-screen red pulse over everything until the charger is in.
// one process, two 1x1 buffers, ~2 commits/s, no polling beyond a timer.
// cc -O2 battery-flash.c <scanner glue> -lwayland-client
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <poll.h>
#include <wayland-client.h>
#include "wlr-layer-shell-unstable-v1-client-protocol.h"
#include "viewporter-client-protocol.h"
#include "single-pixel-buffer-v1-client-protocol.h"

#define ON_MS 380
#define OFF_MS 380
#define CHECK_MS 2000
#define THRESHOLD 27

static struct wl_compositor *comp;
static struct zwlr_layer_shell_v1 *shell;
static struct wp_viewporter *viewporter;
static struct wp_single_pixel_buffer_manager_v1 *spb;
static struct wl_region *empty;
static struct wl_buffer *b_red, *b_clear;

struct out {
	struct out *next;
	uint32_t name;
	struct wl_output *output;
	struct wl_surface *surface;
	struct zwlr_layer_surface_v1 *layer;
	struct wp_viewport *viewport;
};
static struct out *outs;

static void paint(struct out *o, int on)
{
	wl_surface_attach(o->surface, on ? b_red : b_clear, 0, 0);
	wl_surface_damage_buffer(o->surface, 0, 0, 1, 1);
	wl_surface_commit(o->surface);
}

static void ls_configure(void *d, struct zwlr_layer_surface_v1 *ls, uint32_t serial,
			 uint32_t w, uint32_t h)
{
	struct out *o = d;
	zwlr_layer_surface_v1_ack_configure(ls, serial);
	if (!w || !h)
		return;
	wp_viewport_set_destination(o->viewport, w, h);
	paint(o, 1);
}

static void ls_closed(void *d, struct zwlr_layer_surface_v1 *ls) { (void)d; (void)ls; }

static const struct zwlr_layer_surface_v1_listener ls_listener = { ls_configure, ls_closed };

static void add_output(uint32_t name, struct wl_output *output)
{
	struct out *o = calloc(1, sizeof *o);
	o->name = name;
	o->output = output;
	o->surface = wl_compositor_create_surface(comp);
	wl_surface_set_input_region(o->surface, empty);
	o->viewport = wp_viewporter_get_viewport(viewporter, o->surface);
	o->layer = zwlr_layer_shell_v1_get_layer_surface(shell, o->surface, output,
			ZWLR_LAYER_SHELL_V1_LAYER_OVERLAY, "battery-flash");
	zwlr_layer_surface_v1_add_listener(o->layer, &ls_listener, o);
	zwlr_layer_surface_v1_set_anchor(o->layer,
		ZWLR_LAYER_SURFACE_V1_ANCHOR_TOP | ZWLR_LAYER_SURFACE_V1_ANCHOR_BOTTOM |
		ZWLR_LAYER_SURFACE_V1_ANCHOR_LEFT | ZWLR_LAYER_SURFACE_V1_ANCHOR_RIGHT);
	zwlr_layer_surface_v1_set_exclusive_zone(o->layer, -1);
	zwlr_layer_surface_v1_set_keyboard_interactivity(o->layer, 0);
	wl_surface_commit(o->surface);
	o->next = outs;
	outs = o;
}

static void drop_output(uint32_t name)
{
	for (struct out **p = &outs; *p; p = &(*p)->next) {
		if ((*p)->name != name)
			continue;
		struct out *o = *p;
		*p = o->next;
		zwlr_layer_surface_v1_destroy(o->layer);
		wp_viewport_destroy(o->viewport);
		wl_surface_destroy(o->surface);
		wl_output_destroy(o->output);
		free(o);
		return;
	}
}

static int pending_outputs[16];
static int n_pending;

static void global(void *d, struct wl_registry *reg, uint32_t name, const char *iface,
		   uint32_t ver)
{
	(void)d; (void)ver;
	if (!strcmp(iface, wl_compositor_interface.name))
		comp = wl_registry_bind(reg, name, &wl_compositor_interface, 4);
	else if (!strcmp(iface, zwlr_layer_shell_v1_interface.name))
		shell = wl_registry_bind(reg, name, &zwlr_layer_shell_v1_interface, 1);
	else if (!strcmp(iface, wp_viewporter_interface.name))
		viewporter = wl_registry_bind(reg, name, &wp_viewporter_interface, 1);
	else if (!strcmp(iface, wp_single_pixel_buffer_manager_v1_interface.name))
		spb = wl_registry_bind(reg, name, &wp_single_pixel_buffer_manager_v1_interface, 1);
	else if (!strcmp(iface, wl_output_interface.name)) {
		if (comp && shell)
			add_output(name, wl_registry_bind(reg, name, &wl_output_interface, 1));
		else if (n_pending < 16)
			pending_outputs[n_pending++] = (int)name;
	}
}

static void global_remove(void *d, struct wl_registry *reg, uint32_t name)
{
	(void)d; (void)reg;
	drop_output(name);
}

static const struct wl_registry_listener reg_listener = { global, global_remove };

static int force;

static int charged(void)
{
	if (force)
		return 0;
	char buf[32];
	FILE *f = fopen("/sys/class/power_supply/BAT0/status", "r");
	if (f) {
		buf[0] = 0;
		if (fgets(buf, sizeof buf, f) && (!strncmp(buf, "Charging", 8) ||
						  !strncmp(buf, "Full", 4))) {
			fclose(f);
			return 1;
		}
		fclose(f);
	}
	f = fopen("/sys/class/power_supply/BAT0/capacity", "r");
	if (!f)
		return 0;
	int cap = -1;
	if (fscanf(f, "%d", &cap) != 1)
		cap = -1;
	fclose(f);
	return cap >= THRESHOLD;
}

int main(int argc, char **argv)
{
	force = argc > 1 && !strcmp(argv[1], "--force");
	struct wl_display *dpy = wl_display_connect(NULL);
	if (!dpy)
		return 1;
	struct wl_registry *reg = wl_display_get_registry(dpy);
	wl_registry_add_listener(reg, &reg_listener, NULL);
	wl_display_roundtrip(dpy);
	if (!comp || !shell || !viewporter || !spb) {
		fputs("battery-flash: missing wayland globals\n", stderr);
		return 1;
	}
	empty = wl_compositor_create_region(comp);
	// premultiplied: 55% red over everything
	b_red = wp_single_pixel_buffer_manager_v1_create_u32_rgba_buffer(spb, 0x8ccccccc, 0, 0, 0x8ccccccc);
	b_clear = wp_single_pixel_buffer_manager_v1_create_u32_rgba_buffer(spb, 0, 0, 0, 0);
	for (int i = 0; i < n_pending; i++)
		add_output((uint32_t)pending_outputs[i],
			   wl_registry_bind(reg, (uint32_t)pending_outputs[i],
					    &wl_output_interface, 1));
	wl_display_roundtrip(dpy);

	struct pollfd pfd = { .fd = wl_display_get_fd(dpy), .events = POLLIN };
	int on = 1, since_check = 0;
	for (;;) {
		int wait = on ? ON_MS : OFF_MS;
		wl_display_flush(dpy);
		int r = poll(&pfd, 1, wait);
		if (r < 0)
			return 1;
		if (r > 0) {
			if (wl_display_dispatch(dpy) < 0)
				return 1;
			continue;
		}
		on = !on;
		for (struct out *o = outs; o; o = o->next)
			paint(o, on);
		since_check += wait;
		if (since_check >= CHECK_MS) {
			since_check = 0;
			if (charged())
				return 0;
		}
	}
}
