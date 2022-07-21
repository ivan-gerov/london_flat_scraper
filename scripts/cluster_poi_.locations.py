import json

from vincenty import vincenty

FOURSPACE = 0
MANUAL = 0
CONSOLIDATED = 0


class ClustersBase:
    NAME: str

    def __init__(self):
        with open(f"datasets/manual/{self.NAME}_locations.json") as f:
            self.manual_data = json.load(f)

        with open(f"datasets/fourspace/{self.NAME}.json") as f:
            fourspace_data = json.load(f)

        geopoints = []
        geopoints.extend(self.process_manual_geopoints())
        geopoints.extend(
            [
                tuple(address["geocodes"]["main"].values())
                for address in fourspace_data
                if address["geocodes"].get("main")
            ]
        )
        clusters = self.create_clusters(geopoints)
        with open(f"pois/{self.NAME}.json", "w") as f:
            json.dump(clusters, f)

        global MANUAL
        global FOURSPACE
        global CONSOLIDATED
        MANUAL += len(self.manual_data)
        FOURSPACE += len(fourspace_data)
        CONSOLIDATED += len(clusters)

    def process_manual_geopoints(self):
        raise Exception("Not implemented!")

    @staticmethod
    def create_clusters(coordinates, distance=0.100):
        coordinates = set(coordinates)
        clusters = []
        while coordinates:
            locus = coordinates.pop()
            cluster = [x for x in coordinates if vincenty(locus, x) <= distance]
            cluster.append(locus)
            if len(cluster) > 1:
                for x in cluster:
                    if x != locus:
                        coordinates.remove(x)
                coordinate = ClustersBase.find_cluster_midpoint(cluster)
            else:
                coordinate = cluster[0]
            clusters.append(coordinate)

        return clusters

    @staticmethod
    def find_cluster_midpoint(cluster):
        lat = []
        long = []
        for l in cluster:
            lat.append(l[0])
            long.append(l[1])
        return sum(lat) / len(lat), sum(long) / len(long)


class AldiClusters(ClustersBase):
    NAME = "aldi"

    def process_manual_geopoints(self):
        return [tuple(address["latlng"].values()) for address in self.manual_data]


class AsdaClusters(ClustersBase):
    NAME = "asda"

    def process_manual_geopoints(self):
        coordinates = []
        for address in self.manual_data:
            latlon = tuple([float(el) for el in address.split(",")])
            coordinates.append(latlon)
        return coordinates


class BootsClusters(ClustersBase):
    NAME = "boots"

    def process_manual_geopoints(self):
        return [
            (float(address["latitude"]), float(address["longitude"]))
            for address in self.manual_data
        ]


class LidlClusters(ClustersBase):
    NAME = "lidl"

    def process_manual_geopoints(self):
        coordinates = []
        for address in self.manual_data:
            latlon = tuple([float(el) for el in address["location"].values()])
            coordinates.append(latlon)
        return coordinates


class SainsburrysClusters(LidlClusters):
    NAME = "sainsburrys"


class SuperdrugClusters(ClustersBase):
    NAME = "superdrug"

    def process_manual_geopoints(self):
        return [tuple(address["geoPoint"].values()) for address in self.manual_data]


class TescoCLusters(AsdaClusters):
    NAME = "tesco"


if __name__ == "__main__":
    cluster_classes = [
        AldiClusters,
        AsdaClusters,
        BootsClusters,
        LidlClusters,
        SainsburrysClusters,
        SuperdrugClusters,
        TescoCLusters,
    ]
    geopoints = 0
    clusters = 0
    for cluster_class in cluster_classes:
        cluster_class()

    print(
        [
            f"Manual: {MANUAL}",
            f"Fourspace: {FOURSPACE}",
            f"Combined: {MANUAL + FOURSPACE}",
            f"Consolidated Geopoints: {CONSOLIDATED}",
        ]
    )
