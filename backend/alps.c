// SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)

#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <dirent.h>
#include <ctype.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "alps_skel.h"
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "sched_common.h"
#include <arpa/inet.h>
#include <sys/socket.h>
#include <string.h>

#define HEIGHT 14
#define WIDTH  6
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8083
#define BUFFER_SIZE 1024

#define STRUCT_FORMAT '<100Q'
typedef struct {
	unsigned long data[100];
} message_t;


static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
	return vfprintf(stderr, format, args);
}

static void bump_memlock_rlimit(void)
{
	struct rlimit rlim_new = {
		.rlim_cur	= RLIM_INFINITY,
		.rlim_max	= RLIM_INFINITY,
	};

	if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
		fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
		exit(1);
	}
}

int main(int argc, char **argv)
{
	libbpf_set_print(libbpf_print_fn);
	bump_memlock_rlimit();

	char *filename = "seal_bpf.o";
	struct bpf_object *obj;
	struct bpf_link *links[3];
	struct bpf_program *prog;
	int map_fd = 0;
	obj = bpf_object__open_file(filename, NULL);
	if (libbpf_get_error(obj)) {
		printf("ERROR: opening BPF object file failed\n");
	}

	/* load BPF program */
	if (bpf_object__load(obj)) {
		printf("ERROR: loading BPF object file failed\n");
		goto cleanup;
	}
	func_sched_item temp = {23,23};
	int result;
	int i = 0;
	func_sched_item value;
	
	map_fd = bpf_object__find_map_fd_by_name(obj, "func_map");
	if (map_fd < 0){
        	printf("can not find map\n");
		goto cleanup;
	}

	bpf_object__for_each_program(prog, obj) {
		links[i] = bpf_program__attach(prog);
		if (libbpf_get_error(links[i])) {
			fprintf(stderr, "ERROR: bpf_program__attach failed\n");
			links[i] = NULL;
			goto cleanup;
		}
		i++;
	}

    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        perror("Error creating socket");
        exit(1);
    }
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    server_addr.sin_port = htons(SERVER_PORT);

    if (connect(client_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
    	perror("Error connecting to server");
    	exit(1);
    }
    message_t msg;
	for (int i = 0; i < 100; ++i){
		msg.data[i] = 1 + i;
	}
	msg.data[0] = 100000001;
    int key;
	unsigned long priority;
	unsigned long ts;
	for(int j = 0; j < 25; j++){
		int key = j + 1;
		priority = msg.data[j] % 1000000;
		ts = msg.data[j] - priority;
		temp.p1 = priority;
		temp.p2 = ts;
		bpf_map_update_elem(map_fd, &(key), &temp, BPF_ANY);
	}


	for (i = 0; i < 1000000; i++) {
        if (send(client_socket, (void*)&msg, sizeof(msg), 0) < 0) {
        	perror("Error sending message");
            	exit(1);
        }

        message_t response;
        if (recv(client_socket, (void*)&response, sizeof(response), 0) < 0) {
        	perror("Error receiving response");
            	exit(1);
        }

		msg = response;
		for(int j = 0; j < 100; j++){
			int key = j + 1;
			priority = response.data[j] % 1000000;
			ts = response.data[j] - priority;
			temp.p1 = priority;
			temp.p2 = ts;
			bpf_map_update_elem(map_fd, &(key), &temp, BPF_ANY);
        }
		sleep(10);
	}
	close(client_socket);
	return 0;
cleanup:
	for (i--; i >= 0; i--)
		bpf_link__destroy(links[i]);

	bpf_object__close(obj);
	return 0;
}
