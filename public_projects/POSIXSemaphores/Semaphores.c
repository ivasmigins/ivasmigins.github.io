#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define buffLonersSize 10
#define buffGroupSize 10
#define buffPremiumSize 10

// The amount of seats offered for each group. Row 1 would be the premium spaces. Row 2 and 3 are normal spaces.
#define normalSpaces 6
#define premiumSpaces 3

// The amount of time each thread sleeps after inputting.
#define sleepLoners 2
#define sleepGroups 1
#define sleepPremium 2
#define sleepCart 10

sem_t riders, spacesGroups,  spacesLoners, spacesPremium, mutex;
int groupBuffer[buffGroupSize] = {0};
int lonerBuffer[buffLonersSize] = {0};
int premiumBuffer[buffPremiumSize] = {0};

int inGroup = 0, inLoner = 0, outGroup = 0, outLoner = 0, inPremium = 0, outPremium = 0; // Used to track indexes
int lonersStarving = 0; // Increases every time a cart leaves without loners

// To track queue sizes
int currentPremiumCount = 0;
int currentGroupCount = 0;
int currentLonerCount = 0;

void insertPremium(int *pickedPremium, int *room) {
    while (*pickedPremium < 3 && *room >= 1 && currentPremiumCount > 0) {
        int groupSize = premiumBuffer[outPremium];
        if (*room >= groupSize && groupSize >= 1) {
            *room -= groupSize;
            premiumBuffer[outPremium] = 0;
            outPremium = (outPremium + 1) % buffPremiumSize;
            currentPremiumCount--;
            sem_post(&spacesPremium);
            (*pickedPremium)++;
            printf(" a premium group of %d,", groupSize);
        } else break;
    }
}

void insertGroups(int *pickedGroups, int *room) {
    while (*pickedGroups < 3 && *room >= 2 && currentGroupCount > 0) {
        int groupSize = groupBuffer[outGroup];
        if (*room >= groupSize && groupSize >= 2) {
            *room -= groupSize;
            groupBuffer[outGroup] = 0;
            outGroup = (outGroup + 1) % buffGroupSize;
            currentGroupCount--;
            sem_post(&spacesGroups);
            (*pickedGroups)++;
            printf(" a group of %d,", groupSize);
        } else break;
    }
}

void insertLoners(int *pickedLoners, int *room) {
    while (*room > 0 && currentLonerCount > 0) {
        int lonerSize = lonerBuffer[outLoner];
        if (lonerSize == 1) {
            *room -= 1;
            lonerBuffer[outLoner] = 0;
            outLoner = (outLoner + 1) % buffLonersSize;
            currentLonerCount--;
            sem_post(&spacesLoners);
            (*pickedLoners)++;
        } else break;
    }
}

void *cartThread() {
    while (1) {
        sleep(sleepCart);

        sem_wait(&riders);
        sem_wait(&mutex);

        int room = normalSpaces;
        int premiumRoom = premiumSpaces;

        int pickedLoners = 0;
        int pickedGroups = 0;
        int pickedPremium = 0;

        if (lonersStarving >= 2) { // 2 carts left with no loners
            room = 1;
            printf("\nLoners were starved! Attempting to insert at least 1 loner.");
            insertLoners(&pickedLoners, &room);
            room = normalSpaces - pickedLoners; // 1 loner should have been added if there is any on the queue
            if (pickedLoners != 0) lonersStarving = 0; // Reset the signal only if a loner was added.
        }

        printf("\nThe cart departed with:");

        insertPremium(&pickedPremium, &premiumRoom);

        // If we want to fill the whole cart, in case the premium queue is empty
//		if (pickedPremium == 0) {
//			room += premiumRoom; // Keep in mind I'm still only picking 3 groups max, so a lot of loners might enter if this is enabled
//		}

        insertGroups(&pickedGroups, &room);
        insertLoners(&pickedLoners, &room);

        if (pickedGroups > 0 || pickedPremium > 0) printf(" and");
        if (pickedLoners == 0) lonersStarving++;
        else lonersStarving = 0;

        printf(" %d loner(s). \n\n",  pickedLoners);

        printf("The queues values at this moment are: \nPremium Queue: %d\nGroups Queue: %d\nLoners Queue: %d\n\n",
               currentPremiumCount,
               currentGroupCount,
               currentLonerCount);

        sem_post(&mutex);
    }

    pthread_exit(0);
}

void *groupThread() {
    while (1) {
        int r = rand() % (5 + 1 - 2) + 2; // From 2-5

        sem_wait(&spacesGroups);
        sem_wait(&mutex);

        groupBuffer[inGroup] = r;
        currentGroupCount++;
        printf("[GROUP] GROUP OF %d ENTERED.\n", r);
        inGroup = (inGroup + 1) % buffGroupSize;

        sem_post(&mutex);
        sem_post(&riders);

        sleep(sleepGroups);
    }

    pthread_exit(0);
}

void *lonerThread() {
    while (1) {
        sem_wait(&spacesLoners);
        sem_wait(&mutex);

        lonerBuffer[inLoner] = 1;
        currentLonerCount++;
        printf("[LONER] LONER ENTERED.\n");
        inLoner = (inLoner + 1) % buffLonersSize;

        sem_post(&mutex);
        sem_post(&riders);
        sleep(sleepLoners);
    }

    pthread_exit(0);
}

void *premiumThread() {
    while (1) {
        int r = rand() % (3 + 1 - 1) + 1; // Can be 1 user or a group up to 3

        sem_wait(&spacesPremium);
        sem_wait(&mutex);

        premiumBuffer[inPremium] = r;
        currentPremiumCount++;
        printf("[PREMIUM] GROUP OF %d ENTERED.\n", r);
        inPremium = (inPremium + 1) % buffPremiumSize;

        sem_post(&mutex);
        sem_post(&riders);

        sleep(sleepPremium);
    }

    pthread_exit(0);
}

int main(int argc, char * argv[]) {
    int targ[4];
    pthread_t thread[4];

    sem_init(&mutex, 0, 1);
    sem_init(&spacesGroups, 0, buffGroupSize);
    sem_init(&spacesLoners, 0, buffLonersSize);
    sem_init(&spacesPremium, 0, buffPremiumSize);
    sem_init(&riders, 0, 0);

    pthread_create(&thread[0], NULL, &groupThread, (void *) &targ[0]);
    pthread_create(&thread[1], NULL, &lonerThread, (void *) &targ[1]);
    pthread_create(&thread[2], NULL, &premiumThread, (void *) &targ[2]);
    pthread_create(&thread[3], NULL, &cartThread,(void *) &targ[3]);

    for(int i = 0; i < 4; i++) {
        pthread_join(thread[i], NULL);
    }

    sem_destroy(&spacesGroups);
    sem_destroy(&spacesLoners);
    sem_destroy(&spacesPremium);
    sem_destroy(&riders);
    sem_destroy(&mutex);

    return 0;
}